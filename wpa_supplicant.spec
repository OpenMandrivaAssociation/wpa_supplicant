Summary:	Linux WPA Supplicant (IEEE 802.1X, WPA, WPA2, RSN, IEEE 802.11i)
Name:		wpa_supplicant
Version:	0.6.1
Release:	%mkrel 1
License:	GPL
Group:		Communications
URL:		http://hostap.epitest.fi/wpa_supplicant/
Source0:	http://hostap.epitest.fi/releases/wpa_supplicant-%{version}.tar.gz
Source1:	wpa-config
BuildRequires:	libopenssl-devel
BuildRequires:	pcsc-lite-devel
BuildRequires:	doxygen
BuildRequires:	qt3-devel
BuildRequires:	madwifi-source
Requires(pre):	rpm-helper
Requires(post):	rpm-helper
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

%package -n wpa_gui
Group: System/Configuration/Networking
Summary: Graphical tool for wpa_supplicant
%description -n wpa_gui
wpa_gui is a QT frontend for wpa_supplicant.
wpa_supplicant is a WPA Supplicant for Linux, BSD and Windows with
support for WPA and WPA2 (IEEE 802.11i / RSN).

%prep
%setup -q -n %{name}-%{version}
pushd wpa_supplicant
# (blino) comment all "network = { }" blocks
perl -pi -e '$_ = "# $_" if /^\s*network\s*=\s*{/ .. /^\s*}/' wpa_supplicant.conf
cp %{SOURCE1} .config
popd

%build
pushd wpa_supplicant
make
export QTDIR=%{_prefix}/lib/qt3
pushd wpa_gui
 qmake
 make
popd
popd

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_sysconfdir}

pushd wpa_supplicant
cp wpa_supplicant %{buildroot}/%{_sbindir}
cp wpa_cli %{buildroot}/%{_sbindir}
cp wpa_passphrase %{buildroot}/%{_sbindir}
cp wpa_supplicant.conf %{buildroot}%{_sysconfdir}
cp wpa_gui/wpa_gui %{buildroot}%{_sbindir}
popd

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc wpa_supplicant/ChangeLog wpa_supplicant/README wpa_supplicant/eap_testing.txt wpa_supplicant/todo.txt
%attr(0600,root,daemon) %config(noreplace) %{_sysconfdir}/wpa_supplicant.conf
%{_sbindir}/wpa_cli
%{_sbindir}/wpa_passphrase
%{_sbindir}/wpa_supplicant

%files -n wpa_gui
%{_sbindir}/wpa_gui
