%define desktop_dir     %{_datadir}/applications
%define autostart_dir   %{_sysconfdir}/xdg/autostart

Name:           pyarachnecdl
Version:        1.0
Release:        1%{?dist}
Summary:        Arachne Configuration Downloader
License:        GPLv3
URL:            https://github.com/nieslony/pyarachnecdl
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  systemd-rpm-macros
BuildRequires:  desktop-file-utils

Recommends:     NetworkManager-openvpn

Obsoletes:      ArachneConfigDownloader

%{?python_enable_dependency_generator}

%description
Download OpenVPN configuration from Arachne server, a configuration tool for
OpenVPN.

%prep
%autosetup

%build
%py3_build

%install
%py3_install
mkdir -pv %{buildroot}/%{desktop_dir}
touch %{buildroot}/%{desktop_dir}/%{name}.desktop
desktop-file-edit --set-name=%{name} \
    --set-generic-name="Arachne Config Downloader" \
    --set-icon=%{python3_sitelib}/%{name}/data/arachne-green.svg \
    --set-key=Type --set-value=Application \
    --set-key=Exec --set-value=%{name} \
    %{buildroot}/%{desktop_dir}/%{name}.desktop

mkdir -pv %{buildroot}/%{autostart_dir}
touch %{buildroot}/%{autostart_dir}/%{name}.desktop
desktop-file-edit --set-name=%{name} \
    --set-generic-name="Arachne Config Downloader" \
    --set-icon=%{python3_sitelib}/%{name}/data/arachne-green.svg \
    --set-key=Type --set-value=Application \
    --set-key=Exec --set-value=%{name} \
    %{buildroot}/%{autostart_dir}/%{name}.desktop

%files
%doc README.md
%license LICENSE
%{_bindir}/pyarachnecdl
%{python3_sitelib}
%{desktop_dir}/%{name}.desktop
%{autostart_dir}/%{name}.desktop

%changelog
* Fri Jun 13 2025 Claas Nieslony <github@nieslony.at> 1.0-1
- new package built with tito

* Mon Jun 02 2025 Claas Nieslony <github@nieslony.at> 0.1
- Initial version of the package
