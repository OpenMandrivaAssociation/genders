%define	major 0
%define libname	%mklibname genders  %{major}
%define develname %mklibname -d genders 

Summary:	Static cluster configuration database
Name:		genders
Version:	1.13
Release:	%mkrel 3
Group:		System/Libraries
License:	GPL
URL:		https://computing.llnl.gov/linux/genders.html
Source0:	http://mesh.dl.sourceforge.net/sourceforge/genders/%{name}-%{version}.tar.gz
BuildRequires:	autoconf
BuildRequires:	byacc
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	libtool
BuildRequires:	perl-devel
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

%package -n	perl-Genders
Summary:	Genders	interface
Group:		Development/Perl

%description -n	perl-Genders
This package provides a perl interface for querying a genders file.

%prep

%setup  -q -n %{name}-%{version}

%build

%configure2_5x \
    --with-genders-file=%{_sysconfdir}/%{name} \
    --with-perl-destdir=%{buildroot}

%make 

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}

%makeinstall_std

install -m0644 genders.sample %{buildroot}%{_sysconfdir}/%{name}

# nuke rpath
chrpath -d %{buildroot}%{perl_sitearch}/auto/Libgenders/Libgenders.so

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
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

%files -n %{develname}
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%{_mandir}/man3/genders*
%{_mandir}/man3/libgenders* 

%files compat
%defattr(-,root,root)
%{_mandir}/man3/gendlib*
%dir %{_prefix}/lib/genders
%{_prefix}/lib/genders/*

%files -n perl-Genders
%defattr(-,root,root)
%{perl_sitearch}/Genders.pm
%{perl_sitearch}/Libgenders.pm
%dir %{perl_sitearch}/auto/Libgenders
%{perl_sitearch}/auto/Libgenders/Libgenders.so
%{_mandir}/man3/Genders*
%{_mandir}/man3/Libgenders*

