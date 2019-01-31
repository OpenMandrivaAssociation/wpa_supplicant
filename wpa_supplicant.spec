%define _disable_lto 1
%define _disable_ld_no_undefined 1

Summary:	Linux WPA Supplicant (IEEE 802.1X, WPA, WPA2, RSN, IEEE 802.11i)
Name:		wpa_supplicant
Version:	2.7
Release:	0.1
# wpa_supplicant itself is dual-licensed under GPLv2 and BSD license, but as we
# link against GPL libraries, we must use GPLv2 license
License:	GPLv2
Group:		Communications
URL:		http://hostap.epitest.fi/wpa_supplicant/
Source0:	http://hostap.epitest.fi/releases/wpa_supplicant-%{version}.tar.gz
Source7:	%{name}.tmpfiles
Patch0:		wpa_supplicant-2.7-fix-undefined-remove-ie.patch
Patch1:		wpa_supplicant-2.2-omv-defconfig.patch
Patch2:		wpa_supplicant-1.0-mga-dbus-service-file-args.patch
# fedora patches
# quiet an annoying and frequent syslog message
Patch3:		wpa_supplicant-2.2-quiet-scan-results-message.patch

BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(gnutls) >= 3.0
BuildRequires:	pkgconfig(libpcsclite)
BuildRequires:	doxygen
BuildRequires:	pkgconfig(libnl-3.0)
BuildRequires:	readline-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(libsystemd)
Requires:	systemd >= 218
Obsoletes:	wpa_supplicant-gui < 2.4

%description
wpa_supplicant is a WPA Supplicant for Linux, BSD and Windows with
support for WPA and WPA2 (IEEE 802.11i / RSN). Supplicant is the IEEE
802.1X/WPA component that is used in the client stations. It
implements key negotiation with a WPA Authenticator and it controls
the roaming and IEEE 802.11 authentication/association of the wlan
driver.

wpa_supplicant is designed to be a "daemon" program that runs in the
background and acts as the backend component controlling the wireless
connection. wpa_supplicant supports separate frontend programs and an
example text-based frontend, wpa_cli, is included with wpa_supplicant.

Supported WPA/IEEE 802.11i features:
    * WPA-PSK ("WPA-Personal")
    * WPA with EAP (e.g., with RADIUS authentication server)
      ("WPA-Enterprise")
    * key management for CCMP, TKIP, WEP104, WEP40
    * WPA and full IEEE 802.11i/RSN/WPA2
    * RSN: PMKSA caching, pre-authentication

See the project web site or the eap_testing.txt file for a complete
list of supported EAP methods (IEEE 802.1X Supplicant), supported
drivers and interoperability testing.

%prep
%setup -1
%apply_patches

cd wpa_supplicant
# (blino) comment all "network = { }" blocks
perl -pi -e '$_ = "# $_" if /^\s*network\s*=\s*{/ .. /^\s*}/' wpa_supplicant.conf
cp defconfig .config
cd -

export CC=%{__cc}
export CXX=%{__cxx}
%build
%setup_compile_flags
# Fix bug #63030: dereferencing type-punned pointer will break strict-aliasing rules [-Werror=strict-aliasing]
export CFLAGS+=" -fno-strict-aliasing -Wno-error=deprecated-declarations"
export CXXFLAGS+=" -fno-strict-aliasing" FFLAGS+=" -fno-strict-aliasing"
export BINDIR=%{_sbindir}
export LIBDIR=%{_libdir}


cd wpa_supplicant
%make
%make eapol_test
cd -

%install
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_sysconfdir}/dbus-1/system.d/
mkdir -p %{buildroot}%{_datadir}/dbus-1/system-services/

install -d %{buildroot}%{_unitdir}/
install -m0644 %{name}/systemd/*.service -D %{buildroot}%{_unitdir}/
install -m0644 %{SOURCE7} -D %{buildroot}%{_tmpfilesdir}/%{name}.conf

cd wpa_supplicant

# binaries
install -d %{buildroot}%{_sbindir}
install -m 755 wpa_supplicant %{buildroot}/%{_sbindir}
install -m 755 wpa_cli %{buildroot}/%{_sbindir}
install -m 755 wpa_passphrase %{buildroot}/%{_sbindir}
install -m 755 eapol_test %{buildroot}%{_sbindir}

# config
install -d -m 755 %{buildroot}%{_sysconfdir}/%{name}
install -m 600 wpa_supplicant.conf %{buildroot}%{_sysconfdir}/%{name}/wpa_supplicant.conf

# dbus
install -d %{buildroot}%{_sysconfdir}/dbus-1/system.d
install -d %{buildroot}%{_datadir}/dbus-1/system-services
install -m 644 dbus/dbus-wpa_supplicant.conf \
    %{buildroot}%{_sysconfdir}/dbus-1/system.d/wpa_supplicant.conf
install -m 644 dbus/fi.epitest.hostap.WPASupplicant.service \
    %{buildroot}%{_datadir}/dbus-1/system-services
install -m 0644 dbus/fi.w1.wpa_supplicant1.service \
     %{buildroot}%{_datadir}/dbus-1/system-services

# man pages
install -d -m 755 %{buildroot}%{_mandir}/man{5,8}
install -m 644 doc/docbook/*.8 %{buildroot}%{_mandir}/man8
install -m 644 doc/docbook/*.5 %{buildroot}%{_mandir}/man5

cd -

%files
%doc wpa_supplicant/README wpa_supplicant/eap_testing.txt wpa_supplicant/todo.txt
%doc wpa_supplicant/README-WPS
%doc wpa_supplicant/examples/*.conf
%attr(0600,root,daemon) %config(noreplace) %{_sysconfdir}/%{name}/wpa_supplicant.conf
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-nl80211@.service
%{_unitdir}/%{name}-wired@.service
%{_unitdir}/%{name}@.service
%{_tmpfilesdir}/%{name}.conf
%{_sbindir}/wpa_cli
%{_sbindir}/wpa_passphrase
%{_sbindir}/wpa_supplicant
%{_sbindir}/eapol_test
%{_sysconfdir}/dbus-1/system.d/wpa_supplicant.conf
%{_datadir}/dbus-1/system-services/fi.epitest.hostap.WPASupplicant.service
%{_datadir}/dbus-1/system-services/fi.w1.wpa_supplicant1.service
%{_mandir}/man8/*
%{_mandir}/man5/*
