# TODO:
# - add modifications for use system avalaible shared adns library.
# - rewrite ipv6 support to work with non-v6 systems
#
# Conditional build:
%bcond_without	ipv6	# disable ipv6 support
#
Summary:	Internet Relay Chat Server
Summary(pl):	Serwer IRC
Name:		ircd-ptlink
Version:	6.19.4
Release:	3
License:	GPL v2
Group:		Daemons
Source0:	ftp://ftp.sunsite.dk/projects/ptlink/ircd/PTlink%{version}.tar.gz
# Source0-md5:	e7c1ac8e0f6eb5486378b84d3949cc2b
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-config.patch
Patch1:		%{name}-link.patch
URL:		http://www.ptlink.net/Coders/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(ircd)
Provides:	user(ircd)
Obsoletes:	bircd
Obsoletes:	ircd
Obsoletes:	ircd-hybrid
Obsoletes:	ircd6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/ircd
%define		_localstatedir	/var/lib/ircd

%description
PTlink is an advanced IRC server, used by the Portuguese PTLink
network It is fast, reliable, and powerful with good support for
services.

%description -l pl
PTlink jest zaawansowanym serwerem IRC-a, u¿ywanym w portugalskiej
sieci PTLink. Jest on szybki, niezawodny i potê¿ny, posiada dobre
wsparcie dla us³ug.

%prep
%setup -q -n PTlink%{version}
%patch0 -p1
%patch1 -p1
mv -f autoconf/{configure.in,acconfig.h} .

%build
cp -f %{_datadir}/automake/config.* autoconf
%{__aclocal}
%{__autoconf}
CFLAGS="%{rpmcflags} %{?debug:-DDEBUGMODE}"
%configure \
	%{?with_ipv6:--enable-ipv6} \
	--enable-utf-8
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/ircd,%{_var}/log/ircd,%{_sysconfdir}} \
	$RPM_BUILD_ROOT{%{_libdir}/ircd/{modules{,/autoload},tools,help},%{_sbindir},%{_mandir}/man8} \
	$RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_localstatedir}}

install src/ircd $RPM_BUILD_ROOT%{_sbindir}/ircd
install tools/fixklines $RPM_BUILD_ROOT%{_sbindir}/fixklines
install doc/simple.conf	$RPM_BUILD_ROOT%{_sysconfdir}/ircd.conf
install samples/main.dconf.sample	$RPM_BUILD_ROOT%{_sysconfdir}/main.dconf
install samples/network.dconf.sample $RPM_BUILD_ROOT%{_sysconfdir}/network.dconf
install doc/ircd.8 $RPM_BUILD_ROOT%{_mandir}/man8
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ircd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ircd

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -f -g 75 ircd
%useradd -g ircd -d /etc/ircd -u 75 -c "IRC service account" -s /bin/true ircd

%post
/sbin/chkconfig --add ircd
%service ircd restart "IRC daemon"

%preun
if [ "$1" = "0" ]; then
	%service ircd stop
	/sbin/chkconfig --del ircd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove ircd
	%groupremove ircd
fi

%files
%defattr(644,root,root,755)
%doc doc/{*.txt,*.conf,server-version-info,Tao-of-IRC.940110} doc_hybrid6/* CHANGES README
%attr(755,root,root) %{_sbindir}/*
%attr(770,root,ircd) %dir %{_sysconfdir}
%attr(660,ircd,ircd) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.conf
%attr(660,ircd,ircd) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.dconf
%attr(754,root,root) /etc/rc.d/init.d/ircd
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ircd
%dir %{_libdir}/ircd
%attr(770,root,ircd) %dir %{_var}/log/ircd
%attr(770,root,ircd) %dir %{_localstatedir}
%{_mandir}/man*/*
