%define dist .el7
Name:		ccsp	
Version:	0.2
Release:	1%{?dist}
Summary:	Simple capacity usage tracker for a ceph or glusterfs cluster

Group:		Applications/System
License:	GPLv3
URL:		https://github.com/pcuzner/ccsp

# download from https://github.com/pcuzner/ccsp
# rename to ccsp-%{version}.tar.gz

Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	python-devel
BuildRequires:	python-setuptools

Requires:	python >= 2.7
Requires:   rrdtool-python


%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%description
RPM to provide a daemon to track space usage of a ceph or glusterfs cluster

%prep
%setup -q -n %{name}


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot} --install-scripts %{_bindir}
mkdir -p %{buildroot}/etc/systemd/system
mkdir -p %{buildroot}/var/ccsp
install -m 0644 startup/rhs-usage.service %{buildroot}/etc/systemd/system

#mkdir -p %{buildroot}%{_mandir}/man8
#install -m 0644 gstatus.8 %{buildroot}%{_mandir}/man8/
#gzip %{buildroot}%{_mandir}/man8/gstatus.8


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc README
%{_bindir}/rhs_usage
%config /etc/rhs-usage.conf
%{python2_sitelib}/rhsusage/
%{python2_sitelib}/rhs_usage-%{version}-*.egg-info/
%dir /var/ccsp
/var/www/ccsp
/etc/systemd/system/rhs-usage.service


%changelog
* Wed Jan 06 2016 Paul Cuzner <pcuzner@redhat.com> 0.1
- Created
