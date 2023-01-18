# death_dice

A new Flutter project.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.


https://pub.dev/packages/flutter_amplify_sdk/versions/0.0.1
https://docs.amplify.aws/start/q/integration/flutter/

flutter packages pub run flutter_launcher_icons:main
flutter pub pub run flutter_native_splash:create


To upload to google play store
- Install java JDK for access to keystore (https://www.oracle.com/java/technologies/downloads/#jdk19-windows)
- Add the path to the PATH environment variable (C:\Program Files\Java\jdk-19\bin)
- Create keystore (https://docs.flutter.dev/deployment/android#create-an-upload-keystore):
```
cd ~
keytool -genkey -v -keystore upload-keystore.jks -storetype JKS -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```
- Reference keystore at [project]/android/key.properties, (no backslashes, only forward slahes, no quotes) (https://docs.flutter.dev/deployment/android#reference-the-keystore-from-the-app)
- Update build.gradle (applicationId can't use com.example)
- flutter build appbundle
- in play.google.com/console, create a new App
- Testing -> internal Testing -> Create new release
- Upload bundle ([project]\build\app\outputs\bundle\release)
- Release, copy link for testers

Subsequent releases
- edit pubspec.yaml release version (bump the last 2 digits, the + is used by google)
- flutter build appbundle
- in play.google.com/console, select internal testing, edit release



