%define DT_version 0.53
%define DTLocale_version 0.44
%define DTTimeZone_version 1.08

Name:           perl-DateTime
# must now be 0.xx00 to preserve upgrade path:
Version:        %{DT_version}00
Release:        1%{?dist}
Epoch:          1
Summary:        Date and time objects
License:        GPL+ or Artistic
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/DateTime/
Source0:        http://www.cpan.org/authors/id/D/DR/DROLSKY/DateTime-%{DT_version}.tar.gz
Source1:        http://www.cpan.org/authors/id/D/DR/DROLSKY/DateTime-TimeZone-%{DTTimeZone_version}.tar.gz
Source2:        http://www.cpan.org/authors/id/D/DR/DROLSKY/DateTime-Locale-%{DTLocale_version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:  perl(Class::ISA)
BuildRequires:  perl(Class::Singleton) >= 1.03
BuildRequires:  perl(ExtUtils::CBuilder)
BuildRequires:  perl(File::Find::Rule)
BuildRequires:  perl(List::MoreUtils)
BuildRequires:  perl(Module::Build) >= 0.35
# or better:
#BuildRequires:  perl(Module::Build) >= 0.36
BuildRequires:  perl(Params::Validate) >= 0.91
BuildRequires:  perl(Pod::Man) >= 1.14
BuildRequires:  perl(Test::Exception)
BuildRequires:  perl(Test::More) >= 0.34
BuildRequires:  perl(Test::Output)
BuildRequires:  perl(Test::Pod) >= 1.14
BuildRequires:  perl(Test::Pod::Coverage) >= 1.08
Requires:       perl(Class::Singleton) >= 1.03
Requires:       perl(Params::Validate) >= 0.91
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Provides:       perl-DateTime-TimeZone = %{DTTimeZone_version}
Provides:       perl-DateTime-Locale = %{DTLocale_version}
Provides:       perl(DateTimePP)
Provides:       perl(DateTimePPExtra)

%{?filter_setup:
%filter_from_requires /^perl(Win32::/d
# drop the unversioned provide:
%filter_from_provides /^perl(DateTime)$/d
%?perl_default_filter
}

%description
DateTime is a class for the representation of date/time combinations, and
is part of the Perl DateTime project. For details on this project please
see http://datetime.perl.org/. The DateTime site has a FAQ which may help
answer many "how do I do X?" questions. The FAQ is at
http://datetime.perl.org/?FAQ.

%prep
%setup -q -T -c -n DateTimeBundle -a 0
%setup -q -T -D -n DateTimeBundle -a 1
%setup -q -T -D -n DateTimeBundle -a 2

(
f=DateTime-%{DT_version}/lib/DateTime/LeapSecond.pm
iconv -f iso-8859-1 -t utf-8 $f > $f.utf8 && mv $f.utf8 $f
)

%build
cd DateTime-Locale-%{DTLocale_version}
%{__perl} Build.PL installdirs=vendor
./Build
cd -

cd DateTime-TimeZone-%{DTTimeZone_version}
%{__perl} Build.PL installdirs=vendor
./Build
cd -

cd DateTime-%{DT_version}
PERLLIB=../DateTime-Locale-%{DTLocale_version}/blib/lib
PERLLIB=$PERLLIB:../DateTime-TimeZone-%{DTTimeZone_version}/blib/lib
export PERLLIB
%{__perl} Build.PL installdirs=vendor optimize="$RPM_OPT_FLAGS"
./Build
cd -

%install
rm -rf $RPM_BUILD_ROOT

for d in DateTime-Locale-%{DTLocale_version} \
	 DateTime-TimeZone-%{DTTimeZone_version} \
	 DateTime-%{DT_version}; do
  cd $d
  ./Build install destdir=$RPM_BUILD_ROOT create_packlist=0
  cd -
done

find $RPM_BUILD_ROOT -type f -name '*.bs' -size 0 -exec rm -f {} \;
find $RPM_BUILD_ROOT -depth -type d -empty -exec rmdir {} \;

%{_fixperms} $RPM_BUILD_ROOT/*


# Move documentation into bundle area
mkdir DT::Locale DT::TimeZone
mv DateTime-%{DT_version}/{CREDITS,Changes,LICENSE,README,TODO} .
mv DateTime-Locale-%{DTLocale_version}/{Changes,LICENSE.cldr} DT::Locale
mv DateTime-TimeZone-%{DTTimeZone_version}/{Changes,README} DT::TimeZone

%check
# Have to use PERL5LIB rather than PERLLIB here because the test scripts
# clobber PERLLIB
PERL5LIB=$(pwd)/DateTime-%{DT_version}/blib/arch:$(pwd)/DateTime-%{DT_version}/blib/lib
PERL5LIB=$PERL5LIB:$(pwd)/DateTime-Locale-%{DTLocale_version}/blib/lib
PERL5LIB=$PERL5LIB:$(pwd)/DateTime-TimeZone-%{DTTimeZone_version}/blib/lib
export PERL5LIB

# Run pod-related tests.
IS_MAINTAINER=1
export IS_MAINTAINER

for d in DateTime-Locale-%{DTLocale_version} \
	 DateTime-TimeZone-%{DTTimeZone_version} \
	 DateTime-%{DT_version}; do
  cd $d
  ./Build test
  cd -
done

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,0755)
%doc CREDITS Changes LICENSE README TODO DT::Locale DT::TimeZone
%{_mandir}/man3/*
# DateTime::TimeZone and DateTime::Locale modules are arch-independent
%{perl_vendorlib}/DateTime/
# DateTime module is arch-specific
%{perl_vendorarch}/auto/*
%{perl_vendorarch}/DateTime/
%{perl_vendorarch}/DateTime*.pm

%changelog
* Fri Jan 15 2010 Stepan Kasal <skasal@redhat.com> - 1:0.5300-1
- new upstream version
- use Build.PL as Makefile.PL no longer exists
- use iconv to recode to utf-8, not a patch
- update BuildRequires
- drop Provides: perl(DateTime::TimeZoneCatalog), it is no longer there
- use filtering macros

* Mon Dec  7 2009 Stepan Kasal <skasal@redhat.com> - 1:0.4501-4
- rebuild against perl 5.10.1

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.4501-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.4501-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 09 2008 Steven Pritchard <steve@kspei.com> 1:0.4501-1
- Update to DateTime 0.4501.

* Mon Nov 10 2008 Steven Pritchard <steve@kspei.com> 1:0.4401-1
- Update to DateTime 0.4401.
- Update to DateTime::Locale 0.42.
- Update to DateTime::TimeZone 0.8301.

* Mon Sep 08 2008 Steven Pritchard <steve@kspei.com> 1:0.4304-2
- Update to DateTime::TimeZone 0.7904.

* Tue Jul 15 2008 Steven Pritchard <steve@kspei.com> 1:0.4304-1
- Update to DateTime 0.4304.
- Update to DateTime::TimeZone 0.78.
- Update to DateTime::Locale 0.41.

* Tue Jul 08 2008 Steven Pritchard <steve@kspei.com> 1:0.4302-2
- Update to DateTime::TimeZone 0.7701.

* Sat May 31 2008 Steven Pritchard <steve@kspei.com> 1:0.4302-1
- Update to DateTime 0.4302.
- Update to DateTime::TimeZone 0.77.
- Update to DateTime::Locale 0.4001.
- BR List::MoreUtils.
- Define IS_MAINTAINER so we run the pod tests.

* Thu May 15 2008 Steven Pritchard <steve@kspei.com> 1:0.42-1
- Update to DateTime 0.42.
- Update to DateTime::TimeZone 0.75.
- Update FAQ URL in description.

* Wed Feb 27 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1:0.41-5
- Rebuild for perl 5.10 (again)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1:0.41-4
- Autorebuild for GCC 4.3

* Thu Jan 24 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1:0.41-3
- rebuild for new perl

* Tue Dec 11 2007 Steven Pritchard <steve@kspei.com> 1:0.41-2
- Update License tag.
- Update to DateTime::TimeZone 0.70.

* Mon Sep 17 2007 Steven Pritchard <steve@kspei.com> 1:0.41-1
- Update to DateTime 0.41.
- Update to DateTime::Locale 0.35.
- Update to DateTime::TimeZone 0.67.

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 1:0.39-2
- Rebuild for selinux ppc32 issue.

* Sun Jul 22 2007 Steven Pritchard <steve@kspei.com> 1:0.39-1
- Update to DateTime 0.39.
- Update to DateTime::TimeZone 0.6603.

* Thu Jul 05 2007 Steven Pritchard <steve@kspei.com> 1:0.38-2
- BR Test::Output.

* Mon Jul 02 2007 Steven Pritchard <steve@kspei.com> 1:0.38-1
- Update to DateTime 0.38.
- Update to DateTime::TimeZone 0.6602.
- BR Test::Pod::Coverage.

* Mon Apr 02 2007 Steven Pritchard <steve@kspei.com> 1:0.37-3
- Drop BR DateTime::Format::* to avoid circular build deps.

* Mon Apr 02 2007 Steven Pritchard <steve@kspei.com> 1:0.37-2
- Filter Win32::TieRegistry dependency.
- Do the provides filter like we do in cpanspec.
- Drop some macro usage.

* Sat Mar 31 2007 Steven Pritchard <steve@kspei.com> 1:0.37-1
- Update to DateTime 0.37.
- Update to DateTime::TimeZone 0.63.

* Tue Mar 13 2007 Steven Pritchard <steve@kspei.com> 1:0.36-2
- Update to DateTime::Locale 0.34.
- Update to DateTime::TimeZone 0.62.

* Mon Jan 22 2007 Steven Pritchard <steve@kspei.com> 1:0.36-1
- Update to Date::Time 0.36.
- Update to DateTime::Locale 0.33.
- Update to DateTime::TimeZone 0.59.

* Fri Nov 03 2006 Steven Pritchard <steve@kspei.com> 1:0.35-1
- Update to DateTime 0.35.
- Update to DateTime::Locale 0.3101.
- LICENSE.icu seems to have been renamed LICENSE.cldr.
- Update to DateTime::TimeZone 0.54.
- Use fixperms macro instead of our own chmod incantation.
- Convert DateTime::LeapSecond to UTF-8 to avoid a rpmlint warning.

* Tue Aug 29 2006 Steven Pritchard <steve@kspei.com> 1:0.34-3
- Update to DateTime::TimeZone 0.48.

* Mon Aug 28 2006 Steven Pritchard <steve@kspei.com> 1:0.34-2
- Update to DateTime::TimeZone 0.47.

* Mon Aug 14 2006 Steven Pritchard <steve@kspei.com> 1:0.34-1
- Update to DateTime 0.34.

* Fri Jul 28 2006 Steven Pritchard <steve@kspei.com> 1:0.32-1
- Update to DateTime 0.32.
- Improve Summary, description, and source URLs.
- Fix find option order.

* Thu Jul 13 2006 Steven Pritchard <steve@kspei.com> 1:0.31-2
- BR DateTime::Format::ICal and DateTime::Format::Strptime for better
  test coverage.

* Wed May 24 2006 Steven Pritchard <steve@kspei.com> 1:0.31-1
- Update DateTime to 0.31.
- Update DateTime::TimeZone to 0.46.

* Mon Feb 27 2006 Steven Pritchard <steve@kspei.com> 1:0.30-3
- Bump Epoch (argh, 0.2901 > 0.30 to rpm)
- Update DateTime::TimeZone to 0.42

* Sat Feb 18 2006 Steven Pritchard <steve@kspei.com> 0.30-2
- Update DateTime::TimeZone to 0.41

* Tue Jan 10 2006 Steven Pritchard <steve@kspei.com> 0.30-1
- Update DateTime to 0.30
- Update DateTime::TimeZone to 0.40

* Fri Sep 16 2005 Paul Howarth <paul@city-fan.org> 0.2901-2
- Unpack each tarball only once
- Use Module::Build's build script where available
- Help each module find the others when needed
- Clean up files list
- Include additional documentation from DT::Locale & DT::TimeZone
- Add BR: perl(File::Find::Rule) & perl(Test::Pod) to improve test coverage
- Remove unversioned provides of perl(DateTime) & perl(DateTime::TimeZone)

* Wed Aug 31 2005 Steven Pritchard <steve@kspei.com> 0.2901-1
- Specfile autogenerated.
