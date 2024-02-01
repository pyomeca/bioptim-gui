import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class ObjectiveTypeRadio extends StatefulWidget {
  const ObjectiveTypeRadio({
    super.key,
    required this.value,
    required this.phaseIndex,
    required this.objectiveIndex,
  });

  final String value;
  final int phaseIndex;
  final int objectiveIndex;

  @override
  ObjectiveTypeRadioState createState() => ObjectiveTypeRadioState();
}

class ObjectiveTypeRadioState extends State<ObjectiveTypeRadio> {
  String _selectedValue = '';

  @override
  void initState() {
    super.initState();
    _selectedValue = widget.value;
  }

  @override
  Widget build(BuildContext context) {
    final valueLabel = {"mayer": "\u2133", "lagrange": "\u2112"};

    return Consumer<OCPData>(builder: (context, data, child) {
      return Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          for (var pair in valueLabel.entries)
            Row(
              children: [
                Radio<String>(
                  value: pair.key,
                  groupValue: _selectedValue,
                  onChanged: (newValue) async {
                    data.updatePenaltyField(
                      widget.phaseIndex,
                      widget.objectiveIndex,
                      Objective,
                      "objective_type",
                      newValue,
                    );

                    setState(() {
                      _selectedValue = newValue!;
                    });
                  },
                ),
                Text(pair.value),
              ],
            ),
        ],
      );
    });
  }
}
