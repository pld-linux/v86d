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
Version:	0.1.9
Release:	2
License:	GPL v2
Group:		Applications/System
Source0:	http://dev.gentoo.org/~spock/projects/uvesafb/archive/%{name}-%{version}.tar.bz2
# Source0-md5:	ebbbc8e7013c9544b6ba6981add43831
Source1:	%{name}-uvesafb.conf
Patch0:		%{name}-system-klibc.patch
Patch1:		%{name}-system-libs.patch
Patch2:		%{name}-klibc-ldflags.patch
URL:		http://dev.gentoo.org/~spock/projects/uvesafb/
BuildRequires:	linux-libc-headers >= 7:2.6.24
%if %{with klibc}
BuildRequires:	klibc-static >= 1.5.8-1
%if %{with x86emu}
BuildRequires:	x86emu-devel(klibc)
%endif
%else
%if %{with x86emu}
BuildRequires:	x86emu-devel
%else
BuildRequires:	lrmi-devel >= 0.10-4
%endif
%endif
%if %{without x86emu}
Requires:	lrmi >= 0.10-4
%endif
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

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
%patch1 -p1
sed -i 's:-g -O2:$(OPTFLAGS):' Makefile
%patch2 -p1

%build
# not ac
./configure \
	--with%{!?with_klibc:out}-klibc \
	--with%{!?with_x86emu:out}-x86emu

%{__make} \
%if %{with klibc}
	LIB=%{_lib} \
%else
	CC="%{__cc}" \
%endif
	OPTFLAGS="%{rpmcflags}%{!?with_x86emu: -I/usr/include/lrmi}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/modprobe.d}

install %{name} $RPM_BUILD_ROOT%{_sbindir}/%{name}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/modprobe.d/uvesafb.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README TODO
%attr(755,root,root) %{_sbindir}/v86d
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/uvesafb.conf
