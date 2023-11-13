# death_dice

This is just a bunch of notes.

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

- make sure terraform apply was performed first, so .env is populated
- edit pubspec.yaml release version (bump the last 2 digits, the + is used by google)
- flutter build appbundle
- in play.google.com/console, select internal testing, edit release
- make sure you terraform apply in 100percentofthetimehotspaghetti.com

CICD

- edit pubspec.yaml release version (bump the last 2 digits, the + is used by google)
- Codemagic for a new build, linked to github
- (requires moving google console to closed testing)

real device 7m30s til disconnect
emulated 11m til disconnect

Installing on IOS

- Install ruby (https://rubyinstaller.org/downloads/)
- Install curl
- Install cocoapods (https://airtdave.medium.com/using-cocoapods-on-windows-dec471735f51)
