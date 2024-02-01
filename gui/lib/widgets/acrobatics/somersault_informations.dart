import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/widgets/utils/positive_float_text_field.dart';
import 'package:bioptim_gui/widgets/utils/positive_integer_text_field.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class SomersaultInformation extends StatelessWidget {
  const SomersaultInformation({
    super.key,
    required this.somersaultIndex,
    required this.width,
  });

  final int somersaultIndex;
  final double width;

  @override
  Widget build(BuildContext context) {
    return Consumer<OCPData>(builder: (context, data, child) {
      final somersaultPhase =
          (data.phasesInfo[somersaultIndex] as SomersaultPhase);
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              SizedBox(
                width: width / 2 - 6,
                child: PositiveIntegerTextField(
                  label: 'Number of shooting points',
                  value: somersaultPhase.nbShootingPoints.toString(),
                  onSubmitted: (newValue) {
                    if (newValue.isNotEmpty) {
                      data.updatePhaseField(
                          somersaultIndex, "nb_shooting_points", newValue);
                    }
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: PositiveFloatTextField(
                  value: somersaultPhase.duration.toString(),
                  label: 'Phase time (s)',
                  onSubmitted: (newValue) {
                    if (newValue.isNotEmpty) {
                      data.updatePhaseField(
                          somersaultIndex, "duration", newValue);
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
