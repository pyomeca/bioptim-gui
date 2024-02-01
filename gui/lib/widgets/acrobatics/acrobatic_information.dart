import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/widgets/acrobatics/collision_checkbox.dart';
import 'package:bioptim_gui/widgets/acrobatics/visual_criteria_checkbox.dart';
import 'package:bioptim_gui/widgets/acrobatics/with_spine_checkbox.dart';
import 'package:bioptim_gui/widgets/utils/positive_float_text_field.dart';
import 'package:bioptim_gui/widgets/utils/positive_integer_text_field.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class AcrobaticInformation extends StatelessWidget {
  const AcrobaticInformation({
    super.key,
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return Consumer<OCPData>(builder: (context, data, child) {
      final acrobaticsData = data as AcrobaticsData;
      return Column(
        children: [
          Row(children: [
            SizedBox(
              width: width / 3 * 2,
              child: PositiveIntegerTextField(
                label: 'Number of somersaults *',
                value: acrobaticsData.nbSomersaults.toString(),
                onSubmitted: (newValue) {
                  if (newValue.isNotEmpty) {
                    data.updateField("nb_somersaults", newValue);
                  }
                },
              ),
            ),
            SizedBox(
              width: width / 3,
              child: Column(children: [
                Row(
                  children: [
                    const SizedBox(width: 4),
                    CollisionCheckbox(
                      defaultValue: acrobaticsData.collisionConstraint,
                    ),
                    const Text("Non-collision"),
                  ],
                ),
                Row(
                  children: [
                    const SizedBox(width: 4),
                    VisualCriteriaCheckbox(
                      defaultValue: acrobaticsData.withVisualCriteria,
                    ),
                    const Text("Visual Criteria"),
                  ],
                ),
                Row(
                  children: [
                    const SizedBox(width: 4),
                    SpineCriteriaCheckbox(
                      defaultValue: acrobaticsData.withSpine,
                    ),
                    const Text("With spine"),
                  ],
                ),
              ]),
            ),
          ]),
          const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                "Number of half twists *",
                textAlign: TextAlign.left,
              )),
          Row(
            children: [
              for (int i = 0; i < acrobaticsData.halfTwists.length; i++)
                SizedBox(
                  width: (width / acrobaticsData.halfTwists.length),
                  child: PositiveIntegerTextField(
                    label: '',
                    color: Colors.red,
                    value: acrobaticsData.halfTwists[i].toString(),
                    onSubmitted: (newValue) {
                      if (newValue.isNotEmpty) {
                        data.updateHalfTwists(i, int.parse(newValue));
                      }
                    },
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              SizedBox(
                width: width / 2 - 6,
                child: PositiveFloatTextField(
                  value: acrobaticsData.finalTime.toString(),
                  label: 'Final time *',
                  onSubmitted: (newValue) {
                    if (newValue.isNotEmpty) {
                      data.updateField("final_time", newValue);
                    }
                  },
                ),
              ),
              const SizedBox(width: 12),
              SizedBox(
                width: width / 2 - 6,
                child: PositiveFloatTextField(
                  value: acrobaticsData.finalTimeMargin.toString(),
                  label: 'Final time margin *',
                  onSubmitted: (newValue) {
                    if (newValue.isNotEmpty) {
                      data.updateField("final_time_margin", newValue);
                    }
                  },
                ),
              ),
            ],
          )
        ],
      );
    });
  }
}
