# TODO
# - thinko: kernel module searches program from /sbin
#   move here (and dependant libs to) /sbin,/%{_libdir} or patch kernel module:
#   linux-2.6.24/drivers/video/uvesafb.c
#
# Conditional build:
%bcond_with	x86emu	# x86emu instead of LRMI/vm86
%bcond_with	klibc	# use klibc for initramfs purposes
#
%ifnarch %{ix86}
%define		with_x86emu	1
%endif
Summary:	uvesafb userspace helper that runs x86 code in an emulated environment
Summary(pl.UTF-8):	Program pomocniczy uvesafb uruchamiający kod x86 w emulowanym środowisku
Name:		v86d
Version:	0.1.3
Release:	1
License:	GPL v2
Group:		Applications/System
Source0:	http://dev.gentoo.org/~spock/projects/uvesafb/archive/%{name}-%{version}.tar.bz2
# Source0-md5:	1c26f40af343bcc465f5832e2c9548d6
Patch0:		%{name}-system-klibc.patch
Patch1:		%{name}-system-libs.patch
URL:		http://dev.gentoo.org/~spock/projects/uvesafb/
BuildRequires:	linux-libc-headers >= 7:2.6.24
%if %{with klibc}
BuildRequires:	klibc-static >= 1.5.8-1
%else
%if %{with x86emu}
BuildRequires:	x86emu-devel
%else
BuildRequires:	lrmi-devel
%endif
%endif
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
v86d is the userspace helper that runs x86 code in an emulated
environment, used by uvesafb Linux kernel driver. Currently it
supports the x86 and x86-64 architectures.

%description -l pl.UTF-8
v86d to działający w przestrzeni użytkownika program pomocniczy
uruchamiający kod x86. Jest wykorzystywany przez sterownik jądra
Linuksa uvesafb. Obecnie obsługuje architektury x86 i x86-64.

%prep
%setup -q
%patch0 -p1
%{?!with_klibc:%patch1 -p1}
sed -i 's:-g -O2:$(OPTFLAGS):' Makefile
# PLD-specific: system-wide v86d resides in /usr/sbin
sed -i 's:/sbin/v86d 0755:/usr/sbin/v86d 0755:' misc/initramfs

%build
# not ac
./configure \
	--with%{!?with_klibc:out}-klibc \
	--with%{!?with_x86emu:out}-x86emu

%{__make} \
	%{!?with_klibc:CC="%{__cc}"} \
	OPTFLAGS="%{rpmcflags}%{!?with_klibc:%{!?with_x86emu: -I/usr/include/lrmi}}"

%install
rm -rf $RPM_BUILD_ROOT

install -D v86d $RPM_BUILD_ROOT%{_sbindir}/v86d
# XXX what uses this in PLD?
install -D misc/initramfs $RPM_BUILD_ROOT%{_datadir}/v86d/initramfs

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README TODO
%attr(755,root,root) %{_sbindir}/v86d
%dir %{_datadir}/v86d
%{_datadir}/v86d/initramfs
