import 'dart:convert';
import 'dart:math';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/decision_variables_type.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/models/variables.dart';
import 'package:bioptim_gui/widgets/utils/animated_expanding_widget.dart';
import 'package:bioptim_gui/widgets/utils/positive_integer_text_field.dart';
import 'package:bioptim_gui/widgets/variables/interpolation_chooser.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;

class DecisionVariableExpander extends StatelessWidget {
  const DecisionVariableExpander({
    super.key,
    required this.decisionVariableType,
    required this.phaseIndex,
    required this.width,
    required this.endpointPrefix,
    this.enableDimension = true,
  });

  final DecisionVariableType decisionVariableType;
  final int phaseIndex;
  final double width;
  final String endpointPrefix;
  final bool enableDimension;

  @override
  Widget build(BuildContext context) {
    return Consumer<OCPData>(builder: (context, data, child) {
      List<Variable> variables =
          decisionVariableType == DecisionVariableType.control
              ? data.phasesInfo[phaseIndex].controlVariables
              : data.phasesInfo[phaseIndex].stateVariables;

      return AnimatedExpandingWidget(
        header: SizedBox(
          width: width,
          height: 50,
          child: Align(
            alignment: Alignment.centerLeft,
            child: Text(
              '$decisionVariableType variables',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          for (int i = 0; i < variables.length; i++)
            _DecisionVariableChooser(
              name: variables[i].name,
              phaseIndex: phaseIndex,
              variableIndex: i,
              decisionVariableType: decisionVariableType,
              width: width,
              endpointPrefix: endpointPrefix,
              enableDimension: enableDimension,
            ),
        ]),
      );
    });
  }
}

class _DecisionVariableChooser extends StatelessWidget {
  const _DecisionVariableChooser({
    required this.name,
    required this.decisionVariableType,
    required this.phaseIndex,
    required this.variableIndex,
    required this.width,
    required this.endpointPrefix,
    required this.enableDimension,
  });

  final String name;
  final int phaseIndex;
  final int variableIndex;
  final DecisionVariableType decisionVariableType;
  final double width;
  final String endpointPrefix;
  final bool enableDimension;

  @override
  Widget build(BuildContext context) {
    return Consumer<OCPData>(builder: (context, data, child) {
      final variable = decisionVariableType == DecisionVariableType.control
          ? data.phasesInfo[phaseIndex].controlVariables[variableIndex]
          : data.phasesInfo[phaseIndex].stateVariables[variableIndex];

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(height: 24),
          Row(
            children: [
              SizedBox(
                width: width * 2 / 3 - 8,
                child: TextField(
                  decoration: const InputDecoration(
                    label: Text('Variable name'),
                    border: OutlineInputBorder(),
                  ),
                  controller: TextEditingController(text: variable.name),
                  enabled: false,
                ),
              ),
              const SizedBox(width: 12),
              SizedBox(
                width: width / 3 - 8,
                child: PositiveIntegerTextField(
                  enabled: enableDimension,
                  label: 'Dimension',
                  value: variable.dimension.toString(),
                  onSubmitted: (value) async {
                    if (value.isNotEmpty) {
                      data.updateDecisionVariableField(
                          phaseIndex,
                          decisionVariableType,
                          variableIndex,
                          "dimension",
                          value);
                    }
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          InterpolationChooser(
            width: width,
            endpointPrefix: endpointPrefix,
            phaseIndex: phaseIndex,
            decisionVariableType: decisionVariableType,
            variableIndex: variableIndex,
            fieldName: "bounds_interpolation_type",
            requestKey: 'interpolation_type',
            titlePrefix: 'Bounds',
            defaultValue: variable.boundsInterpolationType,
          ),
          const SizedBox(height: 12),
          _DataFiller(
            title: 'Min bounds',
            boxWidth: width * 7 / 8 / 3,
            decisionVariableType: decisionVariableType,
            phaseIndex: phaseIndex,
            variableIndex: variableIndex,
            endpointPrefix: endpointPrefix,
          ),
          const SizedBox(height: 12),
          _DataFiller(
            title: 'Max bounds',
            boxWidth: width * 7 / 8 / 3,
            decisionVariableType: decisionVariableType,
            phaseIndex: phaseIndex,
            variableIndex: variableIndex,
            endpointPrefix: endpointPrefix,
          ),
          const SizedBox(height: 32),
          InterpolationChooser(
            width: width,
            endpointPrefix: endpointPrefix,
            phaseIndex: phaseIndex,
            decisionVariableType: decisionVariableType,
            variableIndex: variableIndex,
            fieldName: "initial_guess_interpolation_type",
            requestKey: 'interpolation_type',
            titlePrefix: 'Initial guess',
            defaultValue: variable.initialGuessInterpolationType,
          ),
          const SizedBox(height: 12),
          _DataFiller(
            title: 'Initial guess',
            boxWidth: width * 7 / 8 / 3,
            decisionVariableType: decisionVariableType,
            phaseIndex: phaseIndex,
            variableIndex: variableIndex,
            endpointPrefix: endpointPrefix,
          ),
          const SizedBox(height: 16),
        ],
      );
    });
  }
}

class _DataFiller extends StatelessWidget {
  const _DataFiller({
    required this.title,
    required this.boxWidth,
    required this.decisionVariableType,
    required this.phaseIndex,
    required this.variableIndex,
    required this.endpointPrefix,
  });

  final String title;
  final double boxWidth;
  final DecisionVariableType decisionVariableType;
  final int phaseIndex;
  final int variableIndex;
  final String endpointPrefix;

  Future<http.Response> updateVariableValue(
      int i, int j, String newValue) async {
    final fieldName = title == 'Min bounds'
        ? 'min_bounds'
        : title == 'Max bounds'
            ? 'max_bounds'
            : 'initial_guess';

    final url =
        '${APIConfig.url}/$endpointPrefix/$phaseIndex/${decisionVariableType.toPythonString()}/'
        '$variableIndex/$fieldName';

    final headers = {'Content-Type': 'application/json'};
    final body = json.encode({"x": i, "y": j, "value": newValue});
    final response =
        await http.put(Uri.parse(url), body: body, headers: headers);

    if (response.statusCode == 200) {
      if (kDebugMode) {
        print('$fieldName updated with value: $newValue');
      }
      return response;
    } else {
      throw Exception('Failed to update $fieldName');
    }
  }

// TODO Add a graph that interacts with the matrix. So user can either fill by hand or by graph
  @override
  Widget build(BuildContext context) {
    List<String> getColNames(String interpolationType) {
      switch (interpolationType) {
        case 'CONSTANT_WITH_FIRST_AND_LAST_DIFFERENT':
          return ['First', 'Intermediate', 'Last'];
        case 'CONSTANT':
          return ['All'];
        case 'LINEAR':
          return ['Start', 'Last'];
        default:
          return [];
      }
    }

    return Consumer<OCPData>(builder: (context, data, child) {
      final variable = decisionVariableType == DecisionVariableType.control
          ? data.phasesInfo[phaseIndex].controlVariables[variableIndex]
          : data.phasesInfo[phaseIndex].stateVariables[variableIndex];

      final interpolationType = title == 'Initial guess'
          ? variable.initialGuessInterpolationType
          : variable.boundsInterpolationType;

      final colNames = getColNames(interpolationType);
      final nbCols = colNames.length;

      final bounds = title == 'Min bounds'
          ? variable.bounds.minBounds
          : title == 'Max bounds'
              ? variable.bounds.maxBounds
              : variable.initialGuess;

      return Center(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                for (int i = 0; i < colNames.length; i++)
                  SizedBox(
                    width: boxWidth,
                    child: Text(colNames[i], textAlign: TextAlign.center),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: boxWidth * min(nbCols, 3),
              // TODO GridView does not work well for unknown nbCol... This should be done using an actual for loop
              // TODO Manage when there is more than 3 columns (scrolling?)
              child: GridView.count(
                childAspectRatio: 2.5,
                shrinkWrap: true,
                crossAxisCount: nbCols,
                children: [
                  for (int i = 0; i < variable.dimension; i++)
                    for (int j = 0; j < nbCols; j++)
                      SizedBox(
                        width: 70,
                        child: TextField(
                          decoration: const InputDecoration(
                            border: OutlineInputBorder(),
                          ),
                          controller: TextEditingController(
                              text: bounds[i][j].toString()),
                          onSubmitted: (value) async {
                            if (value.isNotEmpty) {
                              final response =
                                  await updateVariableValue(i, j, value);

                              final newPhases =
                                  (json.decode(response.body) as List<dynamic>);

                              data.updatePhaseInfo(newPhases);
                            }
                          },
                        ),
                      ),
                ],
              ),
            ),
          ],
        ),
      );
    });
  }
}
