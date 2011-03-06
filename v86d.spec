#
# Conditional build:
%bcond_with	x86emu	# x86emu instead of LRMI/vm86
%bcond_without	initrd	# don't build klibc based helper for initrd/initramfs

%ifnarch %{ix86}
%define		with_x86emu	1
%endif
Summary:	uvesafb userspace helper that runs x86 code in an emulated environment
Summary(pl.UTF-8):	Program pomocniczy uvesafb uruchamiający kod x86 w emulowanym środowisku
Name:		v86d
Version:	0.1.10
Release:	1
License:	GPL v2
Group:		Applications/System
Source0:	http://dev.gentoo.org/~spock/projects/uvesafb/archive/%{name}-%{version}.tar.bz2
# Source0-md5:	51c792ba7b874ad8c43f0d3da4cfabe0
Source1:	%{name}-uvesafb.conf
Patch0:		%{name}-system-klibc.patch
Patch1:		%{name}-system-libs.patch
Patch2:		%{name}-klibc-ldflags.patch
URL:		http://dev.gentoo.org/~spock/projects/uvesafb/
BuildRequires:	linux-libc-headers >= 7:2.6.24
%if %{with initrd}
BuildRequires:	klibc-static >= 1.5.8-1
	%if %{with x86emu}
BuildRequires:	x86emu-klibc-devel
	%else
BuildRequires:	lrmi-klibc-devel >= 0.10-6
	%endif
%endif
%if %{with x86emu}
BuildRequires:	x86emu-devel
%else
BuildRequires:	lrmi-devel >= 0.10-4
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

%package initrd
Summary:	uvesafb userspace helper that runs x86 code in an emulated environment - initrd version
Summary(pl.UTF-8):	Program pomocniczy uvesafb uruchamiający kod x86 w emulowanym środowisku - wersja dla initrd
Group:		Base
Requires:	%{name} = %{version}-%{release}

%description initrd
uvesafb userspace helper that runs x86 code in an emulated environment
- initrd version.

%description initrd -l pl.UTF-8
Program pomocniczy uvesafb uruchamiający kod x86 w emulowanym
środowisku - wersja dla initrd.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
sed -i 's:-g -O2:$(OPTFLAGS):' Makefile
%patch2 -p1

%build
%if %{with initrd}
# not ac
./configure \
	--with-klibc \
	--with%{!?with_x86emu:out}-x86emu

%{__make} \
	LIB=%{_lib} \
	CFLAGS="%{rpmcflags} -Os %{!?with_x86emu:-I/usr/include/klibc/lrmi}"

mkdir -p initrd
cp v86d initrd/
%{__make} clean
%endif

# not ac
./configure \
	--without-klibc \
	--with%{!?with_x86emu:out}-x86emu

%{__make} \
	CC="%{__cc}" \
	OPTFLAGS="%{rpmcflags} %{!?with_x86emu:-I/usr/include/lrmi}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/modprobe.d}

install %{name} $RPM_BUILD_ROOT%{_sbindir}/%{name}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/modprobe.d/uvesafb.conf

%if %{with initrd}
install -d $RPM_BUILD_ROOT%{_libdir}/initrd
install initrd/%{name} $RPM_BUILD_ROOT%{_libdir}/initrd
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README TODO
%attr(755,root,root) %{_sbindir}/v86d
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/uvesafb.conf

%if %{with initrd}
%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/initrd/v86d
%endif
