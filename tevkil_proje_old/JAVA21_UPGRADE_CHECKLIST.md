# Java 21 LTS Upgrade Checklist

## 📋 Current Status

✅ **Gradle Configuration**: Already set to Java 21 compatibility
✅ **Build Files**: All configured for `JavaVersion.VERSION_21`
❌ **JDK 21 Installation**: Not installed (currently using JDK 25)
⚠️ **Recommendation**: Install Java 21 LTS for long-term support

---

## 🎯 Why Java 21 LTS?

| Feature | Java 21 (LTS) | Java 25 (Current) |
|---------|---------------|-------------------|
| **Support Period** | Until Sept 2031 (8 years) | Until March 2026 (6 months) |
| **Stability** | Long-term support | Short-term feature release |
| **Production Use** | ✅ Recommended | ⚠️ Not recommended |
| **Android Support** | ✅ Full support | ⚠️ May have issues |

---

## 🔧 Step-by-Step Upgrade Process

### Step 1: Install Java 21 LTS

#### Option A: Eclipse Temurin (Recommended - Free & Open Source)
1. Visit: https://adoptium.net/temurin/releases/?version=21
2. Download: **Windows x64 MSI** installer
3. During installation:
   - ✅ Check "Set JAVA_HOME variable"
   - ✅ Check "Add to PATH"
   - ✅ Check "Associate .jar files"
4. Default install path: `C:\Program Files\Eclipse Adoptium\jdk-21.x.x.x-hotspot`

#### Option B: Microsoft Build of OpenJDK
1. Visit: https://learn.microsoft.com/en-us/java/openjdk/download#openjdk-21
2. Download: **Windows x64 MSI**
3. Follow installation wizard

#### Option C: Oracle JDK 21
1. Visit: https://www.oracle.com/java/technologies/downloads/#java21
2. Download: **Windows x64 Installer**
3. Note: May require Oracle license for production

### Step 2: Run the Automated Setup Script

```powershell
# Run from project root
.\upgrade-to-java21.ps1
```

This script will:
- ✅ Detect your Java 21 installation
- ✅ Update `android/gradle.properties` automatically
- ✅ Test Gradle compatibility
- ✅ Optionally run a clean build

### Step 3: Manual Configuration (if needed)

If you prefer manual setup:

**Edit**: `android/gradle.properties`

```properties
# Add or update this line with your Java 21 path:
org.gradle.java.home=C:\\Program Files\\Eclipse Adoptium\\jdk-21.0.5.11-hotspot
```

### Step 4: Configure Android Studio

1. Open Android Studio
2. **File** → **Project Structure** → **SDK Location**
3. Set **JDK location**: `C:\Program Files\Eclipse Adoptium\jdk-21.x.x.x-hotspot`
4. Click **OK**
5. **File** → **Settings** → **Build, Execution, Deployment** → **Build Tools** → **Gradle**
6. Set **Gradle JDK**: Select "21" from dropdown
7. Click **OK**
8. **File** → **Invalidate Caches / Restart**

### Step 5: Verify Installation

```powershell
# Check Java version
java -version
# Should show: java version "21.0.x"

# Check Gradle uses Java 21
cd android
.\gradlew --version
# "Launcher JVM" should show version 21.x.x
```

### Step 6: Build & Test

```powershell
# Clean build
cd android
.\gradlew clean

# Debug build
.\gradlew assembleDebug

# Release build (if keystore configured)
.\gradlew assembleRelease

# Run tests
.\gradlew test
```

---

## ✅ Verification Checklist

After upgrade, verify these items:

- [ ] `java -version` shows Java 21.x.x
- [ ] `.\gradlew --version` shows JVM version 21.x.x
- [ ] `android/gradle.properties` has correct `org.gradle.java.home` path
- [ ] Android Studio shows JDK 21 in Project Structure
- [ ] Android Studio Gradle settings use JDK 21
- [ ] `.\gradlew clean assembleDebug` completes successfully
- [ ] No "Unsupported class file major version" errors
- [ ] App runs on emulator/device without issues

---

## 📊 Current Project Configuration

### Files Already Configured for Java 21:

#### ✅ `android/build.gradle`
```gradle
tasks.withType(JavaCompile).configureEach {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}
```

#### ✅ `android/app/build.gradle`
```gradle
compileOptions {
    sourceCompatibility JavaVersion.VERSION_21
    targetCompatibility JavaVersion.VERSION_21
}
```

#### ✅ `android/app/capacitor.build.gradle`
```gradle
sourceCompatibility JavaVersion.VERSION_21
targetCompatibility JavaVersion.VERSION_21
```

### Android Gradle Plugin
- **Version**: 8.7.2 ✅ (Supports Java 21)
- **Compatibility**: Full support for Java 21

---

## 🔍 Troubleshooting

### Issue: "Unsupported class file major version 65"
**Cause**: Gradle is using Java 17 or lower
**Solution**: 
```powershell
# Verify Gradle JVM version
cd android
.\gradlew --version

# Update gradle.properties
# Set: org.gradle.java.home=C:\\Program Files\\Eclipse Adoptium\\jdk-21.x.x.x-hotspot
```

### Issue: "JAVA_HOME is set to an invalid directory"
**Solution**:
```powershell
# Check JAVA_HOME
$env:JAVA_HOME

# Set it temporarily
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-21.0.5.11-hotspot"

# Set it permanently (run as Administrator)
[System.Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-21.0.5.11-hotspot", "Machine")
```

### Issue: Android Studio not detecting Java 21
**Solution**:
1. Close Android Studio completely
2. Update `gradle.properties` with correct path
3. Restart Android Studio
4. **File** → **Invalidate Caches / Restart**

### Issue: Build fails after upgrade
**Solution**:
```powershell
# Clean all Gradle caches
cd android
.\gradlew clean
Remove-Item -Recurse -Force .gradle
Remove-Item -Recurse -Force build
Remove-Item -Recurse -Force app/build

# Rebuild
.\gradlew assembleDebug
```

---

## 🚀 Benefits of Java 21

### Language Features
- ✨ **Virtual Threads** (Project Loom) - Better concurrency
- ✨ **Pattern Matching for switch** - Cleaner code
- ✨ **Record Patterns** - Better data handling
- ✨ **Sequenced Collections** - Ordered collections API
- ✨ **String Templates** (Preview) - String interpolation

### Performance
- ⚡ **ZGC** improvements - Better garbage collection
- ⚡ **G1GC** enhancements - Lower latency
- ⚡ Faster startup time
- ⚡ Reduced memory footprint

### Security
- 🔒 Latest security patches
- 🔒 Enhanced cryptography support
- 🔒 Long-term security updates until 2031

---

## 📅 Java Version Timeline

| Version | Release Date | End of Support | Type |
|---------|--------------|----------------|------|
| Java 8 | March 2014 | Dec 2030 | LTS ✅ |
| Java 11 | Sept 2018 | Sept 2026 | LTS ✅ |
| Java 17 | Sept 2021 | Sept 2029 | LTS ✅ |
| **Java 21** | **Sept 2023** | **Sept 2031** | **LTS ✅** |
| Java 25 | Sept 2025 | March 2026 | Feature ⚠️ |

---

## 📝 Additional Resources

- [Java 21 Documentation](https://docs.oracle.com/en/java/javase/21/)
- [Eclipse Temurin Downloads](https://adoptium.net/temurin/releases/?version=21)
- [Android Gradle Plugin Compatibility](https://developer.android.com/build/releases/gradle-plugin)
- [Capacitor Android Guide](https://capacitorjs.com/docs/android)

---

**Last Updated**: October 28, 2025
**Project**: Tevkil Platform
**Current Java**: 25.0.1 → **Target**: 21.0.x LTS
