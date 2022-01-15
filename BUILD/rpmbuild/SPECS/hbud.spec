Name:		com.github.swanux.hbud
Version:	0.3.0
Release:	1%{?dist}
Summary:	Simple music / video player and karaoke app written in Pytho and GTK - Because why not

License:	GPLv3+
URL:		https://swanux.github.io/hbud.html
Source0:	hbud.tar.xz

BuildRequires:	python3-devel
Requires:	gstreamer1-libav
Requires:	gstreamer1-plugins-good
Requires:	gstreamer1-plugins-bad-free
Requires:	gstreamer1-plugins-ugly
Requires:	libchromaprint
Requires:	gstreamer1-plugins-good-gtk
Requires:	python3-gobject
Requires:	python3-dbus
Requires:	python3

BuildArch:	noarch

%description
Simple music / video player and karaoke app written in Pytho and GTK - Because why not

%prep
%autosetup


%build


%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/usr/share/hbud/
mkdir -p %{buildroot}/usr/share/applications/
cp -R hbud/ %{buildroot}/usr/share/hbud/
cp -R com.github.swanux.hbud %{buildroot}/usr/share/hbud/
cp -R modules/ %{buildroot}/usr/share/hbud/
cp -R com.github.swanux.hbud.desktop %{buildroot}/usr/share/applications/

cat > %{buildroot}/%{_bindir}/%{name} <<-EOF
#!/bin/bash
/usr/bin/python /usr/share/hbud/%{name}
EOF
chmod 0755 %{buildroot}/%{_bindir}/%{name}


%files
%dir /usr/share/hbud/
%{_bindir}/%{name}
/usr/share/applications/com.github.swanux.hbud.desktop
/usr/share/hbud/*


%changelog
* Sat Jan 15 2022 Dániel Kolozsi - 0.3.0
- Initial release
