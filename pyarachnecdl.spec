Name:       pyarachnecdl
Version:    0.1
Release:    1%{?dist}
Summary:    Arachne Configuration Downloader
License:    GPLv3
URL:        https://github.com/nieslony/pyarachnecdl
Source0:    %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  systemd-rpm-macros

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

%files
%doc README.md
%license LICENSE
%{_bindir}/pyarachnecdl
%{python3_sitelib}

%changelog
* Mon Jun 02 2025 Claas Nieslony <github@nieslony.at> 0.1
- Initial version of the package
