# TODO:
# - add modyfications for use system avalaible shared adns library.
# - rewrite ipv6 support to work with non-v6 systems
#
# Conditional build:
%bcond_without	ipv6	# disable ipv6 support
#
Summary:	Internet Relay Chat Server
Summary(pl):	Serwer IRC
Name:		ircd-ptlink
Version:	6.15.1
Release:	4
License:	GPL v2
Group:		Daemons
Source0:	http://dl.sourceforge.net/ptlinksoft/PTlink%{version}.tar.gz
# Source0-md5:	bb5bdbe38e7a3e7a6a9fc3b27387e77a
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-config.patch
Patch1:		%{name}-makefile.patch
Patch2:		%{name}-link.patch
URL:		http://www.ptlink.net/Coders/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	zlib-devel
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	ircd
Obsoletes:	ircd6
Obsoletes:	ircd-hybrid
Obsoletes:	bircd

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
%patch2 -p1

%build
cp -f %{_datadir}/automake/config.* autoconf
%{__aclocal}
%{__autoconf}
CFLAGS="%{rpmcflags} %{?debug:-DDEBUGMODE}"
%configure \
	%{?with_ipv6:--enable-ipv6}
%{__make} \
	LIBDIR=%{_libdir}

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
if [ -n "`getgid ircd`" ]; then
	if [ "`getgid ircd`" != "75" ]; then
		echo "Error: group ircd doesn't have gid=75. Correct this before installing ircd." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -f -g 75 ircd 2> /dev/null
fi
if [ -n "`id -u ircd 2>/dev/null`" ]; then
	if [ "`id -u ircd`" != "75" ]; then
		echo "Error: user ircd doesn't have uid=75. Correct this before installing ircd." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -g ircd -d /etc/ircd -u 75 -c "IRC service account" -s /bin/true ircd 2> /dev/null
fi

%post
/sbin/chkconfig --add ircd
if [ -f /var/lock/subsys/ircd ]; then
	/etc/rc.d/init.d/ircd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/ircd start\" to start IRC daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/ircd ]; then
		/etc/rc.d/init.d/ircd stop 1>&2
	fi
	/sbin/chkconfig --del ircd
fi

%postun
if [ "$1" = "0" ]; then
	/usr/sbin/userdel ircd 2> /dev/null
	/usr/sbin/groupdel ircd 2> /dev/null
fi

%files
%defattr(644,root,root,755)
%doc doc/{*.txt,*.conf,server-version-info,Tao-of-IRC.940110} doc_hybrid6/* CHANGES README
%attr(755,root,root) %{_sbindir}/*
%attr(770,root,ircd) %dir %{_sysconfdir}
%attr(660,ircd,ircd) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ircd.conf
%attr(754,root,root) /etc/rc.d/init.d/ircd
%config(noreplace) %verify(not size mtime md5) /etc/sysconfig/ircd
%dir %{_libdir}/ircd
%attr(770,root,ircd) %dir %{_var}/log/ircd
%attr(770,root,ircd) %dir %{_localstatedir}
%{_mandir}/man*/*
