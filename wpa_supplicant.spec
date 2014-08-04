Summary:	Linux WPA Supplicant (IEEE 802.1X, WPA, WPA2, RSN, IEEE 802.11i)
Name:		wpa_supplicant
Version:	2.2
Release:	3
# wpa_supplicant itself is dual-licensed under GPLv2 and BSD license, but as we
# link against GPL libraries, we must use GPLv2 license
License:	GPLv2
Group:		Communications
URL:		http://hostap.epitest.fi/wpa_supplicant/
Source0:	http://hostap.epitest.fi/releases/wpa_supplicant-%{version}.tar.gz
Source3:	%{name}.service
Source4:	%{name}.sysconfig
Source6:	%{name}.logrotate
Patch1:		wpa_supplicant-2.2-omv-defconfig.patch
# should be safe to just bump MAX_WEP_KEY_LEN to 32
# http://lists.shmoo.com/pipermail/hostap/2005-October/011787.html
Patch2:		wpa_supplicant-0.6.3-WEP232.patch
Patch5:		wpa_supplicant-1.0-mdv-dbus-service-file-args.patch
Patch7:		wpa_supplicant-0.7.3-copy-wpa_scan_results_free-for-wpa_priv.patch
# quiet an annoying and frequent syslog message
Patch8:		wpa_supplicant-2.2-quiet-scan-results-message.patch
# recover from streams of driver disconnect messages (iwl3945)
# rediff ?
#Patch9:		wpa_supplicant-squelch-driver-disconnect-spam.patch
# works around busted drivers by increasing association timeout
Patch10:	wpa_supplicant-assoc-timeout.patch
Patch11:	wpa_supplicant-0.7.3-fix-wpa_priv-eloop_signal_handler-casting.patch
Patch13:	wpa_supplicant-1.0-do-not-call-dbus-functions-with-NULL-path.patch
#Patch14:	wpa_supplicant-1.0-wpagui-gcc47.patch
#Patch from Fedora
Patch16:	wpa_supplicant-2.2-gui-qt4.patch
Patch17:	wpa_supplicant-2.2-libnl3.patch
Requires(post,postun,preun):	rpm-helper
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(gnutls) >= 3.0
BuildRequires:	pkgconfig(libpcsclite)
BuildRequires:	doxygen
BuildRequires:	pkgconfig(QtCore)
BuildRequires:	pkgconfig(libnl-3.0)
BuildRequires:	readline-devel
BuildRequires:	libgcrypt-devel
# http://ndiswrapper.sourceforge.net/wiki/index.php/WPA

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

%package gui
Group:		System/Configuration/Networking
Summary:	Graphical tool for wpa_supplicant
Obsoletes:	wpa_gui

%description gui
wpa_gui is a QT frontend for wpa_supplicant.
wpa_supplicant is a WPA Supplicant for Linux, BSD and Windows with
support for WPA and WPA2 (IEEE 802.11i / RSN).

%prep
%setup -q
%apply_patches

pushd wpa_supplicant
# (blino) comment all "network = { }" blocks
perl -pi -e '$_ = "# $_" if /^\s*network\s*=\s*{/ .. /^\s*}/' wpa_supplicant.conf
cp defconfig .config
popd

export CC=%{__cc}
export CXX=%{__cxx}
%build
%setup_compile_flags
# Fix bug #63030: dereferencing type-punned pointer will break strict-aliasing rules [-Werror=strict-aliasing]
export CFLAGS+=" -fno-strict-aliasing -Wno-error=deprecated-declarations"
export CXXFLAGS+=" -fno-strict-aliasing" FFLAGS+=" -fno-strict-aliasing"
export BINDIR=%{_sbindir}
export LIBDIR=%{_libdir}


pushd wpa_supplicant
%make
%make eapol_test
pushd wpa_gui-qt4
 %qmake_qt4
 %make
popd
popd

%install
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_sysconfdir}/dbus-1/system.d/
mkdir -p %{buildroot}%{_datadir}/dbus-1/system-services/

install -m644 %{SOURCE3} -D %{buildroot}%{_systemunitdir}/%{name}.service
install -m644 %{SOURCE4} -D %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -m644 %{SOURCE6} -D %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

pushd wpa_supplicant

# binaries
install -d %{buildroot}%{_sbindir}
install -m 755 wpa_supplicant %{buildroot}/%{_sbindir}
install -m 755 wpa_cli %{buildroot}/%{_sbindir}
install -m 755 wpa_passphrase %{buildroot}/%{_sbindir}
install -m 755 eapol_test %{buildroot}%{_sbindir}

# gui
install -d %{buildroot}%{_bindir}
install -m 755 wpa_gui-qt4/wpa_gui %{buildroot}%{_bindir}

# config
install -d -m 755 %{buildroot}%{_sysconfdir}
install -m 600 wpa_supplicant.conf %{buildroot}%{_sysconfdir}/wpa_supplicant.conf

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

popd

%post
%systemd_post wpa_supplicant

%preun
%systemd_preun wpa_supplicant

%postun
%systemd_postun wpa_supplicant

%files
%doc wpa_supplicant/ChangeLog wpa_supplicant/README wpa_supplicant/eap_testing.txt wpa_supplicant/todo.txt
%doc wpa_supplicant/README-WPS
%doc wpa_supplicant/examples/*.conf
%attr(0600,root,daemon) %config(noreplace) %{_sysconfdir}/wpa_supplicant.conf
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_systemunitdir}/%{name}.service
%{_sbindir}/wpa_cli
%{_sbindir}/wpa_passphrase
%{_sbindir}/wpa_supplicant
%{_sbindir}/eapol_test
%{_sysconfdir}/dbus-1/system.d/wpa_supplicant.conf
%{_datadir}/dbus-1/system-services/fi.epitest.hostap.WPASupplicant.service
%{_datadir}/dbus-1/system-services/fi.w1.wpa_supplicant1.service
%{_mandir}/man8/*
%{_mandir}/man5/*

%files gui
%{_bindir}/wpa_gui
