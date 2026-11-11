Name:		eclipse-sisu
Version:	0.3.5
Release:	1
Summary:	Eclipse Sisu inject and Plexus integration
Group:		Development/Java
License:	EPL-1.0
URL:		https://github.com/eclipse/sisu.inject
# Tag releases/0.3.5. Gradle 9.9.1 strictly pins org.eclipse.sisu.plexus
# at this version. Maven 3.10 ships 0.9.0.M3.MBI under the same coordinates.
Source0:	https://github.com/eclipse/sisu.inject/archive/refs/tags/releases/%{version}.tar.gz#/sisu-inject-%{version}.tar.gz
Source1:	https://github.com/eclipse/sisu.plexus/archive/refs/tags/releases/%{version}.tar.gz#/sisu-plexus-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(com.google.inject:guice)
BuildRequires:	mvn(com.google.inject.extensions:guice-servlet)
BuildRequires:	mvn(com.google.guava:guava)
BuildRequires:	mvn(javax.inject:javax.inject)
BuildRequires:	mvn(org.slf4j:slf4j-api) >= 2.0.17
BuildRequires:	mvn(javax.annotation:javax.annotation-api)
BuildRequires:	mvn(javax.enterprise:cdi-api)
BuildRequires:	mvn(javax.servlet:javax.servlet-api)
BuildRequires:	mvn(org.osgi:osgi.core)
BuildRequires:	mvn(org.codehaus.plexus:plexus-utils)
BuildRequires:	mvn(org.codehaus.plexus:plexus-classworlds) >= 2.7.0
BuildRequires:	mvn(org.codehaus.plexus:plexus-component-annotations)

%description
org.eclipse.sisu.inject and org.eclipse.sisu.plexus %{version}.
Gradle 9.9.1 pins the Plexus module at this version. The jars are
installed beside the 0.9.0.M3.MBI copies shipped with Maven, using
versioned sysjar indexes so those records stay in place.

%prep
%setup -q -n sisu-project-releases-%{version}
%setup -q -T -D -a 1 -n sisu-project-releases-%{version}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
CP="%{_javadir}/google-guice.jar"
CP="$CP:%{_javadir}/guice/guice-servlet.jar"
CP="$CP:%{_javadir}/atinject.jar"
CP="$CP:%{_javadir}/osgi-core.jar"
CP="$CP:%{_javadir}/slf4j-api.jar"
CP="$CP:%{_javadir}/jakarta-annotations/jakarta.annotation-api.jar"
CP="$CP:%{_javadir}/cdi-api.jar"
CP="$CP:%{_javadir}/javax.servlet-4.0.1.jar"
CP="$CP:%{_javadir}/plexus-utils.jar"
CP="$CP:%{_javadir}/plexus-classworlds-2.7.0.jar"
CP="$CP:%{_javadir}/plexus-containers/plexus-component-annotations.jar"
for jar in ${CP//:/ }; do
	test -s "$jar"
done

compile_mod() {
	src=$1
	out=$2
	expect=$3
	extra=$4
	mkdir -p "$out"
	find "$src" -name '*.java' \
		! -name 'InjectedTest.java' \
		! -name 'InjectedTestCase.java' \
		! -name 'PlexusTestCase.java' > "$out.list"
	test "$(wc -l < "$out.list")" -eq "$expect"
	javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none \
		-cp "$CP:$extra" -d "$out" @"$out.list"
}

compile_mod org.eclipse.sisu.inject/src out/inject 164 ""
compile_mod sisu.plexus-releases-%{version}/org.eclipse.sisu.plexus/src \
	out/plexus 134 out/inject
javap -v -classpath out/inject org.eclipse.sisu.inject.DefaultBeanLocator | grep -F -q 'major version: 52'
javap -v -classpath out/plexus org.eclipse.sisu.plexus.DefaultPlexusBeanLocator | grep -F -q 'major version: 52'

jar_mod() {
	artifact=$1
	classes=$2
	printf 'Manifest-Version: 1.0\nAutomatic-Module-Name: %s\n\n' "$artifact" > "$artifact.mf"
	jar cfm "$artifact.jar" "$artifact.mf" -C "$classes" .
	jar i "$artifact.jar"
}
jar_mod org.eclipse.sisu.inject out/inject
jar_mod org.eclipse.sisu.plexus out/plexus

cat > org.eclipse.sisu.inject.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.eclipse.sisu</groupId>
  <artifactId>org.eclipse.sisu.inject</artifactId>
  <version>0.3.5</version>
  <name>Sisu Inject</name>
  <description>Eclipse Sisu inject 0.3.5.</description>
  <url>https://github.com/eclipse/sisu.inject</url>
  <licenses>
    <license>
      <name>EPL-1.0</name>
      <url>https://www.eclipse.org/legal/epl-v10.html</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.google.inject</groupId>
      <artifactId>guice</artifactId>
      <version>5.1.0</version>
    </dependency>
    <dependency>
      <groupId>com.google.inject.extensions</groupId>
      <artifactId>guice-servlet</artifactId>
      <version>5.1.0</version>
    </dependency>
    <dependency>
      <groupId>javax.inject</groupId>
      <artifactId>javax.inject</artifactId>
      <version>1.0.5</version>
    </dependency>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>2.0.17</version>
    </dependency>
    <dependency>
      <groupId>javax.annotation</groupId>
      <artifactId>javax.annotation-api</artifactId>
      <version>1.3.5</version>
    </dependency>
    <dependency>
      <groupId>javax.enterprise</groupId>
      <artifactId>cdi-api</artifactId>
      <version>2.0.SP1</version>
    </dependency>
    <dependency>
      <groupId>javax.servlet</groupId>
      <artifactId>javax.servlet-api</artifactId>
      <version>4.0.1</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.core</artifactId>
      <version>6.0.0</version>
    </dependency>
  </dependencies>
</project>
EOF

cat > org.eclipse.sisu.plexus.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.eclipse.sisu</groupId>
  <artifactId>org.eclipse.sisu.plexus</artifactId>
  <version>0.3.5</version>
  <name>Sisu Plexus</name>
  <description>Eclipse Sisu Plexus integration 0.3.5.</description>
  <url>https://github.com/eclipse/sisu.plexus</url>
  <licenses>
    <license>
      <name>EPL-1.0</name>
      <url>https://www.eclipse.org/legal/epl-v10.html</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.eclipse.sisu</groupId>
      <artifactId>org.eclipse.sisu.inject</artifactId>
      <version>0.3.5</version>
    </dependency>
    <dependency>
      <groupId>com.google.inject</groupId>
      <artifactId>guice</artifactId>
      <version>5.1.0</version>
    </dependency>
    <dependency>
      <groupId>javax.inject</groupId>
      <artifactId>javax.inject</artifactId>
      <version>1.0.5</version>
    </dependency>
    <dependency>
      <groupId>org.codehaus.plexus</groupId>
      <artifactId>plexus-classworlds</artifactId>
      <version>2.7.0</version>
    </dependency>
    <dependency>
      <groupId>org.codehaus.plexus</groupId>
      <artifactId>plexus-utils</artifactId>
      <version>3.6.2</version>
    </dependency>
    <dependency>
      <groupId>org.codehaus.plexus</groupId>
      <artifactId>plexus-component-annotations</artifactId>
      <version>2.2.0</version>
    </dependency>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>2.0.17</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
set -eo pipefail
: > .mfiles
pin_side() {
	artifact=$1
	index="%{buildroot}%{_datadir}/sysjar/index/org.eclipse.sisu/${artifact}.sysjar"
	sysjar install --buildroot %{buildroot} \
		--artifact "${artifact}.pom:${artifact}.jar" \
		--file-name "${artifact}-%{version}" \
		--filelist ".mfiles-${artifact}"
	/bin/mv "$index" "%{buildroot}%{_datadir}/sysjar/index/org.eclipse.sisu/${artifact}-%{version}.sysjar"
	escaped=$(printf '%s' "$artifact" | sed 's/[.]/\\./g')
	sed -i "s|/${escaped}\\.sysjar|/${artifact}-%{version}.sysjar|" ".mfiles-${artifact}"
	grep -F -q '"version": "%{version}"' "%{buildroot}%{_datadir}/sysjar/index/org.eclipse.sisu/${artifact}-%{version}.sysjar"
	if grep -F -q "/${artifact}.sysjar" ".mfiles-${artifact}"; then
		echo "unversioned index still packaged for $artifact" >&2
		exit 1
	fi
	while IFS= read -r line; do
		grep -qxF -- "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
	done < ".mfiles-${artifact}"
}
pin_side org.eclipse.sisu.inject
pin_side org.eclipse.sisu.plexus

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
INJ=%{buildroot}%{_javadir}/org.eclipse.sisu.inject-%{version}.jar
PLX=%{buildroot}%{_javadir}/org.eclipse.sisu.plexus-%{version}.jar
test -s "$INJ"
test -s "$PLX"
CP="$INJ:$PLX"
CP="$CP:%{_javadir}/google-guice.jar"
CP="$CP:%{_javadir}/guice/guice-servlet.jar"
CP="$CP:%{_javadir}/atinject.jar"
CP="$CP:%{_javadir}/osgi-core.jar"
CP="$CP:%{_javadir}/slf4j-api.jar"
CP="$CP:%{_javadir}/jakarta-annotations/jakarta.annotation-api.jar"
CP="$CP:%{_javadir}/cdi-api.jar"
CP="$CP:%{_javadir}/javax.servlet-4.0.1.jar"
CP="$CP:%{_javadir}/plexus-utils.jar"
CP="$CP:%{_javadir}/plexus-classworlds-2.7.0.jar"
CP="$CP:%{_javadir}/plexus-containers/plexus-component-annotations.jar"
CP="$CP:%{_javadir}/guava.jar"
CP="$CP:%{_javadir}/failureaccess.jar"
mkdir -p check
cat > check/Smoke.java << 'EOF'
import com.google.inject.TypeLiteral;
import org.eclipse.sisu.inject.DefaultBeanLocator;
import org.eclipse.sisu.plexus.DefaultPlexusBeanLocator;
public class Smoke {
	public static void main(String[] args) {
		DefaultBeanLocator beans = new DefaultBeanLocator();
		DefaultPlexusBeanLocator plexus = new DefaultPlexusBeanLocator(beans, "classpath");
		int n = 0;
		for (Object ignored : plexus.locate(TypeLiteral.get(String.class), "role")) {
			n++;
		}
		System.out.println("sisu035_ok " + plexus.getClass().getSimpleName() + " " + n);
	}
}
EOF
javac --release 8 -encoding UTF-8 -proc:none -cp "$CP" -d check check/Smoke.java
java -cp "check:$CP" Smoke > check/check.log
cat check/check.log
grep -F -q 'sisu035_ok DefaultPlexusBeanLocator 0' check/check.log

%files -f .mfiles
%license LICENSE.txt
%doc README.md
