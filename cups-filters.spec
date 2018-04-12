%define _disable_lto 1

%define fontembed_major 1
%define cupsfilters_major 1

%define fontembed %mklibname fontembed %{fontembed_major}
%define fontembeddevel %mklibname fontembed -d
%define cupsfilters %mklibname cupsfilters %{cupsfilters_major}
%define cupsfiltersdevel %mklibname cupsfilters -d

%define beta %{nil}
%define scmrev %{nil}

Name:		cups-filters
Version:	1.20.3
%if "%{beta}" == ""
%if "%{scmrev}" == ""
Release:	1
Source0:	http://openprinting.org/download/%name/%{name}-%{version}.tar.xz
%else
Release:	1.%{scmrev}.1
Source0:	%{name}-%{scmrev}.tar.xz
%endif
%else
%if "%{scmrev}" == ""
Release:	0.%{beta}.1
Source0:	%{name}-%{version}%{beta}.tar.bz2
%else
Release:	0.%{beta}.1.%{scmrev}.1
Source0:	%{name}-%{scmrev}.tar.xz
%endif
%endif
Source1:	cups-browsed.service
Source100:	%{name}.rpmlintrc
Summary:	Print filters for use with CUPS
URL:		http://www.linuxfoundation.org/collaborate/workgroups/openprinting/cups-filters
Group:		System/Printing
BuildRequires:	pkgconfig(libqpdf)
BuildRequires:	pkgconfig(poppler)
BuildRequires:	pkgconfig(poppler-cpp)
BuildRequires:	pkgconfig(lcms2)
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	pkgconfig(ijs)
BuildRequires:	ghostscript-devel >= 9.14
BuildRequires:	cups-devel
BuildRequires:	python-cups
# pdftops needs to be found
BuildRequires:	poppler
BuildRequires:	mupdf
# For a breakdown of the licensing, see COPYING file
# GPLv2:   filters: commandto*, imagetoraster, pdftops, rasterto*,
#                   imagetopdf, pstopdf, texttopdf
#         backends: parallel, serial
# GPLv2+:  filters: gstopxl, textonly, texttops, imagetops
# GPLv3:   filters: bannertopdf
# GPLv3+:  filters: urftopdf
# LGPLv2+:   utils: cups-browsed
# MIT:     filters: gstoraster, pdftoijs, pdftoopvp, pdftopdf, pdftoraster
License: GPLv2 and GPLv2+ and GPLv3 and GPLv3+ and LGPLv2+ and MIT
# For pdftops
Requires:	poppler
Requires:	bc
Conflicts:	cups < 1.7-0.rc1.2
Requires(post,postun):	cups

%track
prog %{name} = {
	url = http://openprinting.org/download/%name/
	regex = %name-(__VER__)\.tar\.xz
	version = %{version}
}

%description
This project provides backends, filters, and other software that was once part
of the core CUPS distribution but is no longer maintained by Apple Inc.

In addition, it contains additional filters and software developed
independently of Apple, especially filters for the PDF-centric printing
workflow introduced by OpenPrinting and a daemon to browse Bonjour broadcasts
of remote CUPS printers to make these printers available locally and to
provide backward compatibility to the old CUPS broadcasting and browsing
of CUPS 1.5.x and older.

%package devel
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{fontembeddevel} = %{EVRD}
Requires:	%{cupsfiltersdevel} = %{EVRD}

%description devel
Development files for %{name}.

%package -n %{fontembed}
Summary:	The fontembed library, part of %{name}
Group:		System/Libraries

%description -n %{fontembed}
The fontembed library, part of %{name}.

%package -n %{fontembeddevel}
Summary:	Development files for the fontembed library, part of %{name}
Group:		Development/C

%description -n %{fontembeddevel}
Development files for the fontembed library, part of %{name}.

%package -n %{cupsfilters}
Summary:	The cupsfilters library, part of %{name}
Group:		System/Libraries

%description -n %{cupsfilters}
The cupsfilters library, part of %{name}.

%package -n %{cupsfiltersdevel}
Summary:	Development files for the cupsfilters library, part of %{name}
Group:		Development/C

%description -n %{cupsfiltersdevel}
Development files for the cupsfilters library, part of %{name}.

%package -n cups-browsed
Summary:	Daemon to allow printer browsing with old versions of cups
Group:		System/Printing
BuildRequires:	pkgconfig(avahi-glib)

%description -n cups-browsed
Daemon to allow printer browsing with old versions of cups.

%prep
%if "%{scmrev}" == ""
%setup -q -n %{name}-%{version}%{beta}
%else
%setup -q -n %{name}
%endif
%apply_patches
./autogen.sh

%configure \
	--disable-static \
	--with-pdftops=pdftops \
	--without-rcdir

%build
%make

%install
%makeinstall_std

# systemd unit file
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_unitdir}

# Symlink for legacy ppds trying to talk to foomatic 2.x
ln -s foomatic-rip %{buildroot}%{_prefix}/lib/cups/filter/cupsomatic

%post
# Restart the CUPS daemon when it is running, but do not start it when it
# is not running.
/bin/systemctl try-restart cups.socket ||:
/bin/systemctl try-restart cups.path ||:
/bin/systemctl try-restart cups.service ||:

%postun
if [ $1 -eq 1 ]; then
	/bin/systemctl try-restart cups.socket ||:
    /bin/systemctl try-restart cups.path ||:
    /bin/systemctl try-restart cups.service ||:
fi

%files
%{_bindir}/ttfread
%{_bindir}/foomatic-rip
%{_bindir}/driverless
%{_prefix}/lib/cups/backend/*
%{_prefix}/lib/cups/driver/*
%{_prefix}/lib/cups/filter/*
%{_datadir}/ppd/cupsfilters
%{_datadir}/cups/ppdc/*
%{_datadir}/cups/mime/cupsfilters.*
%{_datadir}/cups/mime/cupsfilters-mupdf.convs
%{_datadir}/cups/mime/cupsfilters-poppler.convs
%{_datadir}/cups/mime/cupsfilters-ghostscript.convs
%{_datadir}/cups/mime/braille.*
%{_datadir}/cups/drv/*
%{_datadir}/cups/data/*
%{_datadir}/cups/charsets/*
%{_datadir}/cups/banners/*
%{_datadir}/cups/braille/*
%{_mandir}/man1/foomatic-rip.1*
%{_mandir}/man1/driverless.1*

%files -n cups-browsed
%doc %{_docdir}/%{name}
%config(noreplace) %{_sysconfdir}/cups/cups-browsed.conf
%{_sbindir}/cups-browsed
%{_mandir}/man5/cups-browsed.conf.5*
%{_mandir}/man8/cups-browsed.8*
%{_unitdir}/cups-browsed.service

%files -n %{cupsfilters}
%{_libdir}/libcupsfilters.so.%{cupsfilters_major}*

%files -n %{fontembed}
%{_libdir}/libfontembed.so.%{fontembed_major}*

%files devel

%files -n %{cupsfiltersdevel}
%{_includedir}/cupsfilters
%{_libdir}/libcupsfilters.so
%{_libdir}/pkgconfig/libcupsfilters.pc

%files -n %{fontembeddevel}
%{_includedir}/fontembed
%{_libdir}/libfontembed.so
%{_libdir}/pkgconfig/libfontembed.pc
