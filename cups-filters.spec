#define _disable_lto 1
%define beta %{nil}
%define scmrev %{nil}

Name:		cups-filters
Version:	2.0.1
%if "%{beta}" == ""
%if "%{scmrev}" == ""
Release:	2
Source0:	https://github.com/OpenPrinting/cups-filters/releases/download/%{version}/cups-filters-%{version}.tar.xz
%else
Release:	0.%{scmrev}1
Source0:	%{name}-%{scmrev}.tar.xz
%endif
%else
%if "%{scmrev}" == ""
Release:	0.%{beta}1
Source0:	%{name}-%{version}%{beta}.tar.bz2
%else
Release:	0.%{scmrev}1
Source0:	%{name}-%{scmrev}.tar.xz
%endif
%endif
Source100:	%{name}.rpmlintrc
Summary:	Print filters for use with CUPS
URL:		https://www.linuxfoundation.org/collaborate/workgroups/openprinting/cups-filters
Group:		System/Printing
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	slibtool
BuildRequires:	make
BuildRequires:	pkgconfig(com_err)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(libqpdf)
BuildRequires:	pkgconfig(poppler)
BuildRequires:	pkgconfig(poppler-cpp)
BuildRequires:	pkgconfig(lcms2)
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	pkgconfig(ijs)
BuildRequires:	pkgconfig(krb5)
BuildRequires:	pkgconfig(libtiff-4)
BuildRequires:	pkgconfig(avahi-client)
BuildRequires:	pkgconfig(libexif)
BuildRequires:	pkgconfig(libcupsfilters) >= 2.0.0
BuildRequires:	pkgconfig(libppd)
BuildRequires:	font(dejavusans)
BuildRequires:	ghostscript-devel >= 9.14
BuildRequires:	cups-devel
BuildRequires:	gettext-devel
BuildRequires:	python-cups
# pdftops needs to be found
BuildRequires:	poppler
BuildRequires:	mupdf
Requires:	font(dejavusans)
# For a breakdown of the licensing, see COPYING file
# GPLv2:   filters: commandto*, imagetoraster, pdftops, rasterto*,
#                   imagetopdf, pstopdf, texttopdf
#         backends: parallel, serial
# GPLv2+:  filters: gstopxl, textonly, texttops, imagetops
# GPLv3:   filters: bannertopdf
# GPLv3+:  filters: urftopdf
# MIT:     filters: gstoraster, pdftoijs, pdftoopvp, pdftopdf, pdftoraster
License: GPLv2 and GPLv2+ and GPLv3 and GPLv3+ and MIT
# For pdftops
Requires:	poppler
Requires:	bc
Conflicts:	cups < 1.7-0.rc1.2
Requires(post,postun):	cups

%patchlist
cups-filters-1.28.11-clangwarnings.patch
# Can't use C++17 string_view in C++11 mode with clang 16...
#cups-filters-c++17.patch
# From upstream
https://github.com/OpenPrinting/cups-filters/commit/9871a50b5c1f9c2caa2754aac1f5db70c886021b.patch
https://github.com/OpenPrinting/cups-filters/commit/6f811dc27a0de8a731bc85097a181a056454f7dd.patch
https://github.com/OpenPrinting/cups-filters/commit/41c5f2f6139e4d3693c2483ee4281202a80ae451.patch
https://github.com/OpenPrinting/cups-filters/commit/c5ea5f5cf3198ca4f63889f818fac966700604ee.patch
https://github.com/OpenPrinting/cups-filters/commit/9e8572578a09fa8a298023c370e407a3fce58175.patch
https://github.com/OpenPrinting/cups-filters/commit/057b50433074771cce4950caaf5a9db68d0f04be.patch
https://github.com/OpenPrinting/cups-filters/commit/830f6b2db5c30739df5d70cb32ab828ee8b2172d.patch
https://github.com/OpenPrinting/cups-filters/commit/c79ee4b56f81fb3afbaf68ce96308ba52eed9a62.patch
https://github.com/OpenPrinting/cups-filters/commit/b103e2f90f732a959366cdcb63c0abb0774a9c84.patch
https://github.com/OpenPrinting/cups-filters/commit/0fe46c511e81062575b05936f804eb18c9f0a011.patch

%description
This project provides backends, filters, and other software that was once part
of the core CUPS distribution but is no longer maintained by Apple Inc.

In addition, it contains additional filters and software developed
independently of Apple, especially filters for the PDF-centric printing
workflow introduced by OpenPrinting and a daemon to browse Bonjour broadcasts
of remote CUPS printers to make these printers available locally and to
provide backward compatibility to the old CUPS broadcasting and browsing
of CUPS 1.5.x and older.

%prep
%if "%{scmrev}" == ""
%autosetup -p1 -n %{name}-%{version}%{beta}
%else
%autosetup -p1 -n %{name}
%endif
sed -i -e 's,glibtoolize,slibtoolize,g' autogen.sh
./autogen.sh

%configure \
	--disable-static \
	--with-pdftops=pdftops \
	--without-rcdir \
	--enable-avahi \
	--with-browseremoteprotocols=DNSSD,CUPS \
	--enable-auto-setup-driverless

%build
%make_build

%install
%make_install

# Symlink for legacy ppds trying to talk to foomatic 2.x
ln -s foomatic-rip %{buildroot}%{_prefix}/lib/cups/filter/cupsomatic

%post
# Restart the CUPS daemon when it is running, but do not start it when it
# is not running.
/bin/systemctl try-restart --quiet cups.socket ||:
/bin/systemctl try-restart --quiet cups.path ||:
/bin/systemctl try-restart --quiet cups.service ||:

%postun
if [ $1 -eq 1 ]; then
    /bin/systemctl try-restart --quiet cups.socket ||:
    /bin/systemctl try-restart --quiet cups.path ||:
    /bin/systemctl try-restart --quiet cups.service ||:
fi

%files
%doc %{_docdir}/%{name}
%{_bindir}/foomatic-hash
%{_bindir}/foomatic-rip
%{_bindir}/driverless
%{_bindir}/driverless-fax
%{_prefix}/lib/cups/backend/*
%{_prefix}/lib/cups/driver/*
%{_prefix}/lib/cups/filter/*
%{_datadir}/ppd/cupsfilters
%{_datadir}/cups/mime/cupsfilters-universal*
%{_datadir}/cups/mime/cupsfilters.*
%{_datadir}/cups/drv/*
%{_mandir}/man1/foomatic-hash.1*
%{_mandir}/man1/foomatic-rip.1*
%{_mandir}/man1/driverless.1*
%{_datadir}/ppdc
