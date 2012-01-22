%define	major 0
%define libname	%mklibname genders %{major}
%define develname %mklibname -d genders

%define gendersplusplus_libname	%mklibname gendersplusplus 1

Summary:	Static cluster configuration database
Name:		genders
Version:	1.18
Release:	%mkrel 2
Group:		System/Libraries
License:	GPL
URL:		https://computing.llnl.gov/linux/genders.html
Source0:	http://mesh.dl.sourceforge.net/sourceforge/genders/%{name}-%{version}.tar.gz
BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	libtool
BuildRequires:	perl-devel
BuildRequires:	python-devel
BuildRequires:	libstdc++-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
Genders is a static cluster configuration database used for cluster
configuration management.  It is used by a variety of tools and scripts for
management of large clusters.  The genders database is typically replicated
on every node of the cluster. It describes the layout and configuration of
the cluster so that tools and scripts can sense the variations of cluster
nodes. By abstracting this information into a plain text file, it becomes
possible to change the configuration of a cluster by modifying only one file.

%package -n	%{gendersplusplus_libname}
Summary:	Static cluster configuration database C++ library
Group:          System/Libraries

%description -n	%{gendersplusplus_libname}
Genders is a static cluster configuration database used for cluster
configuration management.  It is used by a variety of tools and scripts for
management of large clusters.  The genders database is typically replicated
on every node of the cluster. It describes the layout and configuration of
the cluster so that tools and scripts can sense the variations of cluster
nodes. By abstracting this information into a plain text file, it becomes
possible to change the configuration of a cluster by modifying only one file.

This package contains the C++ bindings for genders.


%package -n	%{develname}
Summary:	Static library and header files for the genders library
Group:		Development/C
Provides:	%{name}-devel = %{version}
Provides:	lib%{name}-devel = %{version}
Requires:	%{libname} = %{version}

%description -n	%{develname}
Genders is a static cluster configuration database used for cluster
configuration management.  It is used by a variety of tools and scripts for
management of large clusters.  The genders database is typically replicated
on every node of the cluster. It describes the layout and configuration of
the cluster so that tools and scripts can sense the variations of cluster
nodes. By abstracting this information into a plain text file, it becomes
possible to change the configuration of a cluster by modifying only one file.

This package contains the static genders library and its header files.

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

%setup  -q -n %{name}-%{version}

%build

%configure2_5x \
    --with-genders-file=%{_sysconfdir}/%{name} \
    --with-perl-site-arch \
    --with-extension-destdir=%{buildroot}

make LD_RUN_PATH=""

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}

%makeinstall_std LD_RUN_PATH=""

install -m0644 genders.sample %{buildroot}%{_sysconfdir}/%{name}

# bork
mv %{buildroot}/usr/local/share/man/man3/Libgenders.3pm %{buildroot}%{_mandir}/man3/Libgenders.3pm

%if %mdkversion < 200900

%post -n %{libname} -p /sbin/ldconfig

%post -n %{gendersplusplus_libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%postun -n %{gendersplusplus_libname} -p /sbin/ldconfig

%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
%defattr(-,root,root)
%doc README NEWS ChangeLog DISCLAIMER DISCLAIMER.UC COPYING TUTORIAL
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}
%{_libdir}/*.so.%{major}*

%files -n %{gendersplusplus_libname}
%defattr(-,root,root)
%{_libdir}/libgendersplusplus.so.1*

%files -n %{develname}
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/*.*a
%{_mandir}/man3/genders*
%{_mandir}/man3/libgenders*

%files compat
%defattr(-,root,root)
%{_mandir}/man3/gendlib*
%dir %{_prefix}/lib/genders
%{_prefix}/lib/genders/*

%files -n perl-Libgenders
%defattr(-,root,root)
%{perl_sitearch}/Genders.pm
%{perl_sitearch}/Libgenders.pm
%dir %{perl_sitearch}/auto/Libgenders
%{perl_sitearch}/auto/Libgenders/Libgenders.so
%{_mandir}/man3/Genders.3pm*
%{_mandir}/man3/Libgenders.3pm*

%files -n python-libgenders
%defattr(-,root,root)
%{python_sitearch}/genders.py
%{python_sitearch}/libgenders-*-py*.egg-info
%{python_sitearch}/libgenders.so
