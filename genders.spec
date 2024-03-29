%define _disable_ld_no_undefined 1
%define _disable_lto 1


%define	major	0
%define	majorpp	2
%define libname	%mklibname genders %{major}
%define libnamepp %mklibname gendersplusplus %{majorpp}
%define devname %mklibname -d genders

Summary:	Static cluster configuration database
Name:		genders
%define oversion 1-28-1
Version:	1.28.1
Release:	3
Group:		System/Libraries
License:	GPLv2
Url:		https://computing.llnl.gov/linux/genders.html
Source0:	https://github.com/chaos/genders/archive/genders-%{oversion}/%{name}-%{oversion}.tar.gz
BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	libtool
BuildRequires:	perl-devel
BuildRequires:	stdc++-devel
BuildRequires:	pkgconfig(python)
BuildRequires:  java-current-devel

%description
Genders is a static cluster configuration database used for cluster
configuration management.  It is used by a variety of tools and scripts for
management of large clusters.  The genders database is typically replicated
on every node of the cluster. It describes the layout and configuration of
the cluster so that tools and scripts can sense the variations of cluster
nodes. By abstracting this information into a plain text file, it becomes
possible to change the configuration of a cluster by modifying only one file.

%package -n	%{libname}
Summary:	Static cluster configuration database library
Group:          System/Libraries

%description -n	%{libname}
This package contains a shared library for %{name}.

%package -n	%{libnamepp}
Summary:	Static cluster configuration database C++ library
Group:          System/Libraries

%description -n	%{libnamepp}
This package contains the C++ bindings for genders.

%package -n	%{devname}
Summary:	Development library and header files for the genders library
Group:		Development/C
Provides:	%{name}-devel = %{version}
Requires:	%{libname} = %{version}
Requires:	%{libnamepp} = %{version}

%description -n	%{devname}
This package contains the development genders library and its header files.

%package	compat
Summary:	Compatability library
Group:		System/Libraries

%description	compat
genders API that is compatible with earlier releases of genders

%package -n	perl-Libgenders
Summary:	Genders	interface
Group:		Development/Perl
Provides:	perl-Genders = %{version}
Obsoletes:	perl-Genders

%description -n	perl-Libgenders
This package provides a perl interface for querying a genders file.

%package -n	python-libgenders
Summary:	Genders	interface
Group:		Development/Python

%description -n	python-libgenders
This package provides a python interface for querying a genders file.

%prep
%setup  -qn %{name}-%{name}-%{oversion}

%build
# fix build on aarch64
autoreconf -vfi -Iconfig

export CPPFLAGS='-I/usr/lib/jvm/java-15-openjdk/include/ -I/usr/lib/jvm/java/include/linux -I../../../src/libgenders'
export PYTHON=%__python3
%configure \
	--disable-static \
	--with-genders-file=%{_sysconfdir}/%{name} \
	--with-perl-site-arch \
	--with-extension-destdir=%{buildroot}

make LD_RUN_PATH=""

%install
install -d %{buildroot}%{_sysconfdir}
%makeinstall_std LD_RUN_PATH=""

install -m0644 genders.sample %{buildroot}%{_sysconfdir}/%{name}

# bork
#mv %{buildroot}/usr/local/share/man/man3/Libgenders.3pm %{buildroot}%{_mandir}/man3/Libgenders.3pm

%files
%doc README NEWS ChangeLog DISCLAIMER DISCLAIMER.UC COPYING TUTORIAL
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}
%{_datadir}/doc/genders-*.*-javadoc/*
%{_bindir}/*
%{_datadir}/java/Genders.jar
%{_libdir}/libGendersjni.so.*
%{_mandir}/man1/*

%files -n %{libname}
%{_libdir}/libgenders.so.%{major}*

%files -n %{libnamepp}
%{_libdir}/libgendersplusplus.so.%{majorpp}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/*.so
%{_mandir}/man3/genders*
%{_mandir}/man3/libgenders*

%files compat
%{_mandir}/man3/gendlib*
%dir %{_prefix}/lib/genders
%{_prefix}/lib/genders/*

%files -n perl-Libgenders
%doc DISCLAIMER DISCLAIMER.UC COPYING
%{_libdir}/perl*/Genders.pm
%{_libdir}/perl*/Libgenders.pm
%{_libdir}/perl*/auto/Libgenders/Libgenders.so
%{_mandir}/man3/Genders.3pm*
%{_mandir}/man3/Libgenders.3pm*

%files -n python-libgenders
%doc DISCLAIMER DISCLAIMER.UC COPYING
%{python_sitearch}/genders.py*
%{python_sitearch}/libgenders-*-py*.egg-info
%{python_sitearch}/libgenders*.so
%{python_sitearch}/__pycache__/*

