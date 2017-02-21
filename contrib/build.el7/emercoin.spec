Name:           Paris
Version:        0.6.0
Release:        1%{dist}
Summary:        Paris Wallet
Group:          Applications/Internet
Vendor:         Paris
License:        GPLv3
URL:            http://www.Paris.com
Source0:        %{name}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:  autoconf automake libtool gcc-c++ openssl-devel >= 1:1.0.2d libdb4-devel libdb4-cxx-devel miniupnpc-devel boost-devel boost-static
Requires:       pwgen openssl >= 1:1.0.2d libdb4 libdb4-cxx miniupnpc logrotate

%description
Paris Wallet

%prep
%setup -q -n Paris

%build
./autogen.sh
./configure
make

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir} $RPM_BUILD_ROOT/etc/Paris $RPM_BUILD_ROOT/etc/ssl/emc $RPM_BUILD_ROOT/var/lib/emc/.Paris $RPM_BUILD_ROOT/usr/lib/systemd/system $RPM_BUILD_ROOT/etc/logrotate.d
%{__install} -m 755 bin/* $RPM_BUILD_ROOT%{_bindir}
%{__install} -m 755 src/Parisd $RPM_BUILD_ROOT%{_bindir}
%{__install} -m 755 src/Paris-cli $RPM_BUILD_ROOT%{_bindir}
%{__install} -m 600 contrib/build.el7/Paris.conf $RPM_BUILD_ROOT/var/lib/emc/.Paris
%{__install} -m 644 contrib/build.el7/Parisd.service $RPM_BUILD_ROOT/usr/lib/systemd/system
%{__install} -m 644 contrib/build.el7/Parisd.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/Parisd

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%pretrans
getent passwd emc >/dev/null && { [ -f /usr/bin/Parisd ] || { echo "Looks like user 'emc' already exists and have to be deleted before continue."; exit 1; }; } || useradd -r -M -d /var/lib/emc -s /bin/false emc

%post
[ $1 == 1 ] && {
  sed -i -e "s/\(^rpcpassword\)\(.*\)/rpcpassword=$(pwgen 64 1)/" /var/lib/emc/.Paris/Paris.conf
  openssl req -nodes -x509 -newkey rsa:4096 -keyout /etc/ssl/emc/Paris.key -out /etc/ssl/emc/Paris.crt -days 3560 -subj /C=US/ST=Oregon/L=Portland/O=IT/CN=Paris.emc
  ln -sf /var/lib/emc/.Paris/Paris.conf /etc/Paris/Paris.conf
  ln -sf /etc/ssl/emc /etc/Paris/certs
  chown emc.emc /etc/ssl/emc/Paris.key /etc/ssl/emc/Paris.crt
  chmod 600 /etc/ssl/emc/Paris.key
} || exit 0

%posttrans
[ -f /var/lib/emc/.Paris/addr.dat ] && { cd /var/lib/emc/.Paris && rm -rf database addr.dat nameindex* blk* *.log .lock; }
sed -i -e 's|rpcallowip=\*|rpcallowip=0.0.0.0/0|' /var/lib/emc/.Paris/Paris.conf
systemctl daemon-reload
systemctl status Parisd >/dev/null && systemctl restart Parisd || exit 0

%preun
[ $1 == 0 ] && {
  systemctl is-enabled Parisd >/dev/null && systemctl disable Parisd >/dev/null || true
  systemctl status Parisd >/dev/null && systemctl stop Parisd >/dev/null || true
  pkill -9 -u emc > /dev/null 2>&1
  getent passwd emc >/dev/null && userdel emc >/dev/null 2>&1 || true
  rm -f /etc/ssl/emc/Paris.key /etc/ssl/emc/Paris.crt /etc/Paris/Paris.conf /etc/Paris/certs
} || exit 0

%files
%doc COPYING
%attr(750,emc,emc) %dir /etc/Paris
%attr(750,emc,emc) %dir /etc/ssl/emc
%attr(700,emc,emc) %dir /var/lib/emc
%attr(700,emc,emc) %dir /var/lib/emc/.Paris
%attr(600,emc,emc) %config(noreplace) /var/lib/emc/.Paris/Paris.conf
%defattr(-,root,root)
%config(noreplace) /etc/logrotate.d/Parisd
%{_bindir}/*
/usr/lib/systemd/system/Parisd.service

%changelog
* Sun Aug 21 2016 Sergii Vakula <sv@Paris.com> 0.5.0
- Rebase to the v0.5.0

* Tue Jun 21 2016 Sergii Vakula <sv@Paris.com> 0.3.7
- Initial release
