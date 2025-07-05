import 'package:flutter/material.dart';

class RuleScreen extends StatefulWidget {
  const RuleScreen({Key? key}) : super(key: key);

  @override
  State<RuleScreen> createState() => _RuleScreenState();
}

class _RuleScreenState extends State<RuleScreen> {
  final AssetImage background = const AssetImage("assets/images/desert-oasis.jpg");
  final AssetImage scroll = const AssetImage("assets/images/ancient-scroll.png");

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: buildAppBar(),
      body: Container(
        constraints: const BoxConstraints.expand(),
        decoration: BoxDecoration(
          image: DecorationImage(
            alignment: Alignment.center,
            colorFilter: ColorFilter.mode(Colors.black.withOpacity(0.5), BlendMode.dstATop),
            fit: BoxFit.cover,
            image: background,
          )
        ),
        child: buildText()
      ),
    );
  
  }
  
  AppBar buildAppBar(){
    return AppBar(
      title: const Text('Rules'),
      backgroundColor: Theme.of(context).primaryColor,
    );
  }

  Widget buildText() {

    var ruleText = '''
The rules for death dice are as follows.

Every player rolls two 6-sided dice. A players score is the sum of all their dice. The player with the highest score wins, everyone else takes a sip of their drink.
    
If players roll doubles, two dice with the same value, they get to roll again.
If players keep rolling the same value, they get to keep rolling, according to the following:
  • Two 1's: Your score is 0. Roll again. If it is 1, 2, or 3, finish your drink. 
  • Four 2's: Hold one drink in each hand until your drink is finished. All drinking from one must be done to the other.
  • Three 3's: Stop playing, go have a shower.
  • Four 4's: Put your head on the table until your drink is finished.
  • Five 5's: Buy something from Wish.com, and give it to Mr Eleven.
  • Six 6's: Stop playing, jump into the nearest large body of water you can find.
  • If two players tie with an 8, they are affected by quantam cockring hands, pulling their wrists down as far as they go until they finish their drink.

If a player has a final score of 11, they are known as Mr Eleven. They have always, and will always be known as Mr Eleven. If Mr Eleven rolls an 11, Mr Eleven wins. Any other players that rolled an 11 in that turn do not lose.

When a player wins 3 turns in a row, they get a 4-sided dice (the death dice). The player with the death dice must always win, otherwise they lose the death dice. If the player with the death dice wins two turns in a row, they upgrade their death dice.

May God have mercy on your souls.
    ''';
    const scaling = 0.6;
    const width = 740 * scaling;
    const height = 995 * scaling;
    return Stack(
      alignment: Alignment.center,
      children: [
        Image(
          image: scroll,
          width: width,
          height: height,
        ),
        SizedBox(
          width: width,
          height: height,
          child: Padding(
            padding: const EdgeInsets.only(left: 78, top: 105, right: 75, bottom: 105),
            child: SingleChildScrollView(
              child: Text(
                ruleText,
                style: const TextStyle(fontFamily: 'Vox Populi')),
            ),
          ),
        ),
      ],
    );
  }

}