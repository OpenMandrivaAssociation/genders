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
Release:	22
Group:		System/Libraries
License:	GPLv2
Url:		https://computing.llnl.gov/linux/genders.html
Source0:	https://github.com/chaos/genders/archive/genders-%{oversion}/%{name}-%{oversion}.tar.gz
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	slibtool
BuildRequires:	make
BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	perl-devel
BuildRequires:	stdc++-devel
# Java optional; skip to keep rebuild focused on perl + C libs
#BuildRequires:  java-current-devel

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
Summary:	Genders interface
Group:		Development/Perl
Provides:	perl-Genders = %{version}
Obsoletes:	perl-Genders < %{version}

%description -n	perl-Libgenders
This package provides a perl interface for querying a genders file.

%prep
%setup -qn %{name}-%{name}-%{oversion}

%build
# Prefer slibtool. Skip autoreconf (needs GNU libtool m4 for automake).
# Upstream ships configure; re-run slibtoolize so ./libtool is slibtool-friendly.
export LIBTOOL=slibtool
if command -v slibtoolize >/dev/null 2>&1; then
  slibtoolize --copy --force || true
fi
# Provide a shell-wrapper libtool for makefiles that run "sh ./libtool"
cat > libtool <<'EOS'
#!/bin/sh
exec slibtool "$@"
EOS
chmod +x libtool
# Prefer slibtool. Hide Makefile.am so %%configure does not re-run automake
# (needs GNU libtool m4). Still get proper RPM CC/CFLAGS via %%configure.
mv Makefile.am Makefile.am._skip_regen 2>/dev/null || true
# Also hide nested Makefile.am that trigger the scan
find . -name Makefile.am -exec mv {} {}._skip_regen \; 2>/dev/null || true
%configure \
	--disable-static \
	--with-genders-file=%{_sysconfdir}/%{name} \
	--with-perl-site-arch \
	--with-python-extensions=no \
	--with-java-extensions=no \
	--with-extension-destdir=%{buildroot}
find . -name 'Makefile.am._skip_regen' | while read f; do mv "$f" "${f%._skip_regen}"; done

# After configure, ensure ./libtool invokes slibtool (not a missing GNU script)
if [ ! -x libtool ] || file libtool | grep -q 'ELF'; then
  cat > libtool <<'EOS'
#!/bin/sh
exec slibtool "$@"
EOS
  chmod +x libtool
elif head -1 libtool | grep -qv '^#!'; then
  # config-only file from slibtoolize: keep and use rlibtool/slibtool via LIBTOOL
  :
fi
%make_build LD_RUN_PATH="" LIBTOOL=slibtool

# Ensure shared libs actually exist after build
find . -name 'libgenders.so*' -o -name 'libgendersplusplus.so*' | head -20
test -n "$(find . -name 'libgenders.so.*' -type f | head -1)"

%install
install -d %{buildroot}%{_sysconfdir}
%make_install LD_RUN_PATH=""

# slibtool install can skip shared libs; copy from .libs explicitly
install -d %{buildroot}%{_libdir}
for so in $(find . -path '*/.libs/libgenders.so*' -type f -o -path '*/.libs/libgenders.so*' -type l); do
  # only real/shared objects and versioned symlinks from the right tree
  case "$so" in
    */libgenders.so|*/libgenders.so.*) install -m755 -p "$so" %{buildroot}%{_libdir}/ || cp -a "$so" %{buildroot}%{_libdir}/ ;;
  esac
done
for so in $(find . -path '*/.libs/libgendersplusplus.so*' \( -type f -o -type l \)); do
  case "$so" in
    */libgendersplusplus.so|*/libgendersplusplus.so.*) install -m755 -p "$so" %{buildroot}%{_libdir}/ || cp -a "$so" %{buildroot}%{_libdir}/ ;;
  esac
done
# Recreate unversioned and soname symlinks
( cd %{buildroot}%{_libdir}
  for base in libgenders libgendersplusplus; do
    real=$(ls -1 ${base}.so.*.*.* 2>/dev/null | head -1)
    [ -n "$real" ] || real=$(ls -1 ${base}.so.[0-9]* 2>/dev/null | head -1)
    [ -n "$real" ] || continue
    soname=$(echo "$real" | sed -E 's/\.so\.[0-9]+\.[0-9]+\.[0-9]+/.so./;s/\.[0-9]+$//' )
    # simpler: libfoo.so.X.Y.Z -> libfoo.so.X and libfoo.so
    maj=$(echo "$real" | sed -n 's/.*\.so\.\([0-9]*\).*/\1/p')
    ln -sfn "$real" ${base}.so.${maj} 2>/dev/null || true
    ln -sfn ${base}.so.${maj} ${base}.so 2>/dev/null || true
  done
  ls -la libgenders* || true
)

# nodeattr binary - force install from .libs or relink
install -d %{buildroot}%{_bindir}
if [ ! -e %{buildroot}%{_bindir}/nodeattr ]; then
  if [ -x src/nodeattr/.libs/nodeattr ]; then
    install -m755 src/nodeattr/.libs/nodeattr %{buildroot}%{_bindir}/nodeattr
  elif [ -f src/nodeattr/nodeattr ]; then
    # may be libtool wrapper; try real binary
    install -m755 src/nodeattr/nodeattr %{buildroot}%{_bindir}/nodeattr 2>/dev/null || true
  fi
fi
if [ ! -e %{buildroot}%{_bindir}/nodeattr ] && [ -f src/nodeattr/nodeattr.c ]; then
  # last resort: compile against staged libs
  cc %{optflags} -o %{buildroot}%{_bindir}/nodeattr src/nodeattr/nodeattr.c     -I./src/libgenders -I./config -L%{buildroot}%{_libdir} -L./src/libgenders/.libs -lgenders     -Wl,-rpath-link,%{buildroot}%{_libdir} 2>/dev/null || true
fi
# if still missing, do not ship empty bindir - drop file entry via dummy not needed if we use optional
if [ ! -e %{buildroot}%{_bindir}/nodeattr ]; then
  echo "ERROR: nodeattr missing"; ls -laR src/nodeattr || true; exit 1
fi

chmod -R u+w %{buildroot} || true
install -m0644 genders.sample %{buildroot}%{_sysconfdir}/%{name}

# Prove required files exist
ls -la %{buildroot}%{_libdir}/libgenders* || true
test -e %{buildroot}%{_libdir}/libgenders.so.%{major} -o -e %{buildroot}%{_libdir}/libgenders.so.%{major}.0.0 \
  -o -n "$(ls %{buildroot}%{_libdir}/libgenders.so.%{major}* 2>/dev/null)"

%files
%doc README NEWS ChangeLog DISCLAIMER DISCLAIMER.UC COPYING TUTORIAL
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}
%{_mandir}/man1/*
%{_bindir}/nodeattr

%files -n %{libname}
%{_libdir}/libgenders.so.%{major}*

%files -n %{libnamepp}
%{_libdir}/libgendersplusplus.so.%{majorpp}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/libgenders.so
%{_libdir}/libgendersplusplus.so
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
