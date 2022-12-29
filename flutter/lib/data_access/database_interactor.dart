import 'package:death_dice/model/exceptions.dart';
import 'package:shared_preferences/shared_preferences.dart';


class DatabaseInteractor {
  static late SharedPreferences prefs;

  DatabaseInteractor();

  Future init() async {
    prefs = await SharedPreferences.getInstance();
  }

  Future write(String key, String value) {
    return prefs.setString(key, value);
  }

  bool containsKey(String key){
    return prefs.containsKey(key);
  }

  String read(String key){
    if (!containsKey(key)) {
      throw KeyNotFoundException(key);
    }
    return prefs.getString(key)!;
  }

  Future delete(String key) {
    return prefs.remove(key);
  }

}
