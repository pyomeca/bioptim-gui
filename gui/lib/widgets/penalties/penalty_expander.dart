import 'dart:convert';

import 'package:bioptim_gui/models/api_config.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:bioptim_gui/widgets/penalties/integration_rule_chooser.dart';
import 'package:bioptim_gui/widgets/penalties/maximize_minimize_radio.dart';
import 'package:bioptim_gui/widgets/penalties/nodes_chooser.dart';
import 'package:bioptim_gui/widgets/penalties/objective_type_radio.dart';
import 'package:bioptim_gui/widgets/penalties/penalty_chooser.dart';
import 'package:bioptim_gui/widgets/utils/animated_expanding_widget.dart';
import 'package:bioptim_gui/widgets/utils/boolean_switch.dart';
import 'package:bioptim_gui/widgets/utils/extensions.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';

class PenaltyExpander extends StatefulWidget {
  const PenaltyExpander({
    super.key,
    required this.penaltyType,
    required this.phaseIndex,
    required this.width,
    required this.endpointPrefix,
  });

  final Type penaltyType;
  final int phaseIndex;
  final double width;
  final String endpointPrefix;

  @override
  PenaltyExpanderState createState() => PenaltyExpanderState();
}

class PenaltyExpanderState extends State<PenaltyExpander> {
  double width = 0;

  @override
  void initState() {
    width = widget.width;
    super.initState();
  }

  String _penaltyTypeToString({required bool plural}) {
    switch (widget.penaltyType) {
      case Objective:
        return plural ? 'Objective functions' : 'Objective function';
      case Constraint:
        return plural ? 'Constraints' : 'Constraint';
      default:
        throw 'Wrong penalty type';
    }
  }

  String _penaltyTypeToEndpoint({required bool plural}) {
    switch (widget.penaltyType) {
      case Objective:
        return plural ? 'objectives' : 'objective';
      case Constraint:
        return plural ? 'constraints' : 'constraint';
      default:
        throw 'Wrong penalty type';
    }
  }

  Future<http.Response> _createPenalties() async {
    final url = Uri.parse(
        '${APIConfig.url}${widget.endpointPrefix}/${widget.phaseIndex}/${_penaltyTypeToEndpoint(plural: true)}');

    final response = await http.post(url);

    if (response.statusCode != 200) throw Exception("Fetch error");

    if (kDebugMode) print("Created a penalty");

    return response;
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<OCPData>(builder: (context, data, child) {
      final penalties = (widget.penaltyType == Constraint)
          ? data.phasesInfo[widget.phaseIndex].constraints
          : data.phasesInfo[widget.phaseIndex].objectives;

      return AnimatedExpandingWidget(
        header: SizedBox(
          width: width,
          height: 50,
          child: Align(
            alignment: Alignment.centerLeft,
            child: Text(
              _penaltyTypeToString(plural: true),
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Align(
              alignment: Alignment.centerRight,
              child: _buildAddButton(
                  _penaltyTypeToString(plural: false).toLowerCase()),
            ),
            const SizedBox(height: 24),
            ...penalties.asMap().keys.map(
                  (index) => Padding(
                    padding: const EdgeInsets.only(bottom: 24.0),
                    child: _PathTile(
                      key: ObjectKey(penalties[index]),
                      phaseIndex: widget.phaseIndex,
                      penaltyIndex: index,
                      width: width,
                      penaltyType: widget.penaltyType,
                      penalty: penalties[index],
                      endpointPrefix: widget.endpointPrefix,
                    ),
                  ),
                ),
            const SizedBox(height: 26),
          ],
        ),
      );
    });
  }

  Consumer<OCPData> _buildAddButton(String name) {
    return Consumer<OCPData>(builder: (context, data, child) {
      return Padding(
        padding: const EdgeInsets.only(right: 18.0, top: 12.0),
        child: InkWell(
          onTap: () async {
            final response = await _createPenalties();
            final newPenalties = (widget.penaltyType == Constraint)
                ? (json.decode(response.body) as List<dynamic>)
                    .map((c) => Constraint.fromJson(c))
                    .toList()
                : (json.decode(response.body) as List<dynamic>)
                    .map((o) => Objective.fromJson(o))
                    .toList();
            data.updatePenalties(
                widget.phaseIndex, widget.penaltyType, newPenalties);
          },
          child: Container(
              padding:
                  const EdgeInsets.only(left: 12, right: 4, top: 2, bottom: 2),
              decoration: BoxDecoration(
                  color: Colors.green, borderRadius: BorderRadius.circular(25)),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'New $name',
                    style: const TextStyle(color: Colors.white),
                  ),
                  const Icon(
                    Icons.add,
                    color: Colors.white,
                  ),
                ],
              )),
        ),
      );
    });
  }
}

class _PathTile extends StatelessWidget {
  const _PathTile({
    required super.key,
    required this.phaseIndex,
    required this.penaltyIndex,
    required this.penaltyType,
    required this.width,
    required this.penalty,
    required this.endpointPrefix,
  });

  final int phaseIndex;
  final int penaltyIndex;
  final Type penaltyType;
  final double width;
  final Penalty penalty;
  final String endpointPrefix;

  String _penaltyTypeToString({required bool plural}) {
    switch (penaltyType) {
      case Objective:
        return plural ? 'Objective functions' : 'Objective function';
      case Constraint:
        return plural ? 'Constraints' : 'Constraint';
      default:
        throw 'Wrong penalty type';
    }
  }

  String _penaltyTypeToEndpoint({required bool plural}) {
    switch (penaltyType) {
      case Objective:
        return plural ? 'objectives' : 'objective';
      case Constraint:
        return plural ? 'constraints' : 'constraint';
      default:
        throw 'Wrong penalty type';
    }
  }

  Future<http.Response> _deletePenalties() async {
    final url = Uri.parse(
        '${APIConfig.url}$endpointPrefix/$phaseIndex/${_penaltyTypeToEndpoint(plural: true)}/$penaltyIndex');

    final response = await http.delete(url);

    if (response.statusCode != 200) throw Exception("Fetch error");

    if (kDebugMode) {
      print('Removed a penalty (${_penaltyTypeToEndpoint(plural: true)})');
    }
    return response;
  }

  @override
  Widget build(BuildContext context) {
    final arguments = penalty.arguments;

    return Consumer<OCPData>(builder: (context, data, child) {
      return AnimatedExpandingWidget(
        header: Center(
          child: Text(
            penaltyType == Objective
                ? data
                    .phasesInfo[phaseIndex].objectives[penaltyIndex].penaltyType
                    .replaceAll("_", " ")
                    .capitalize()
                : data.phasesInfo[phaseIndex].constraints[penaltyIndex]
                    .penaltyType
                    .replaceAll("_", " ")
                    .capitalize(),
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ),
        initialExpandedState: penaltyType == Objective
            ? data.phasesInfo[phaseIndex].objectives[penaltyIndex].expanded
            : data.phasesInfo[phaseIndex].constraints[penaltyIndex].expanded,
        onTapHeader: (isExpanded) {
          if (penaltyType == Constraint) {
            data.phasesInfo[phaseIndex].constraints[penaltyIndex].expanded =
                isExpanded;
          } else {
            data.phasesInfo[phaseIndex].objectives[penaltyIndex].expanded =
                isExpanded;
          }
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 12),
            Row(children: [
              SizedBox(
                width: (penaltyType == Objective)
                    ? width *
                        0.87 // can't get it smaller because of the dropdown's text
                    : width,
                child: PenaltyChooser(
                  title:
                      '${_penaltyTypeToString(plural: false)} ${penaltyIndex + 1} (${penalty.penaltyTypeToString()})',
                  width: width,
                  defaultValue: penalty.penaltyType,
                  endpointPrefix: endpointPrefix,
                  phaseIndex: phaseIndex,
                  penaltyType: penaltyType,
                  penaltyIndex: penaltyIndex,
                ),
              ),
              if (penaltyType == Objective)
                SizedBox(
                  width: width * 0.13,
                  child: ObjectiveTypeRadio(
                    value: (penalty as Objective).objectiveType,
                    phaseIndex: phaseIndex,
                    objectiveIndex: penaltyIndex,
                  ),
                ),
            ]),
            const SizedBox(height: 12),
            for (int i = 0; i < arguments.length; i++)
              Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: Row(
                  children: [
                    SizedBox(
                      width: width,
                      child: TextField(
                        controller: TextEditingController(
                            text: arguments[i].value.toString() == "null"
                                ? ""
                                : arguments[i].value.toString()),
                        decoration: InputDecoration(
                            label: Text(
                                'Argument: ${arguments[i].name} (${arguments[i].type})'),
                            border: const OutlineInputBorder()),
                        // inputFormatters: [FilteringTextInputFormatter.allow()],
                        onSubmitted: (value) => {
                          data.updatePenaltyArgument(
                            phaseIndex,
                            penaltyIndex,
                            arguments[i].name,
                            (value.isEmpty ? null : value),
                            arguments[i].type,
                            i,
                            penaltyType,
                          )
                        },
                      ),
                    ),
                  ],
                ),
              ),
            Row(
              children: [
                SizedBox(
                    width: (penaltyType == Objective) ? width / 2 - 3 : width,
                    child: NodesChooser(
                        width: width,
                        defaultValue: penalty.nodes,
                        endpointPrefix: endpointPrefix,
                        phaseIndex: phaseIndex,
                        penaltyType: penaltyType,
                        penaltyIndex: penaltyIndex,
                        penalty: penalty)),
                if (penaltyType == Objective)
                  SizedBox(
                    width: width / 4 - 3,
                    child: TextField(
                      controller: TextEditingController(
                        text: (penalty as Objective).weight.abs().toString(),
                      ),
                      decoration: const InputDecoration(
                          label: Text('Weight'), border: OutlineInputBorder()),
                      inputFormatters: [
                        FilteringTextInputFormatter.allow(RegExp(r'[0-9\.]')),
                      ],
                      onSubmitted: (value) => {
                        data.updatePenaltyField(
                          phaseIndex,
                          penaltyIndex,
                          penaltyType,
                          "weight",
                          (double.tryParse(value) ?? 0).toString(),
                        ),
                      },
                    ),
                  ),
                if (penaltyType == Objective)
                  SizedBox(
                      width: width / 4 + 6,
                      child: MinMaxRadio(
                        weightValue: (penalty as Objective).weight,
                        phaseIndex: phaseIndex,
                        objectiveIndex: penaltyIndex,
                      )),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: TextEditingController(
                        text: penalty.target.toString() == "null"
                            ? ""
                            : penalty.target.toString()),
                    decoration: const InputDecoration(
                        label: Text('Target'), border: OutlineInputBorder()),
                    inputFormatters: [
                      FilteringTextInputFormatter.allow(RegExp(r'[0-9\.,\[\]]'))
                    ],
                    onSubmitted: (value) => {
                      data.updatePenaltyField(phaseIndex, penaltyIndex,
                          penaltyType, "target", value.tryParseDoubleList())
                    },
                  ),
                ),
              ],
            ),
            // Mayer objectives don't have integration_rule
            if (penaltyType != Objective ||
                (penalty as Objective).objectiveType != "mayer")
              const SizedBox(height: 12),
            if (penaltyType != Objective ||
                (penalty as Objective).objectiveType != "mayer")
              Row(
                children: [
                  SizedBox(
                    width: width,
                    child: IntegrationRuleChooser(
                      width: width,
                      defaultValue: penalty.integrationRule,
                      endpointPrefix: endpointPrefix,
                      phaseIndex: phaseIndex,
                      penaltyType: penaltyType,
                      penaltyIndex: penaltyIndex,
                    ),
                  ),
                ],
              ),
            const SizedBox(height: 12),
            Row(
              children: [
                BooleanSwitch(
                  initialValue: penalty.quadratic,
                  leftText: "Quadratic",
                  width: width / 2 - 6,
                  customOnChanged: (value) => {
                    data.updatePenaltyField(phaseIndex, penaltyIndex,
                        penaltyType, "quadratic", value)
                  },
                ),
                const SizedBox(width: 12),
                BooleanSwitch(
                  initialValue: penalty.expand,
                  leftText: "Expand",
                  width: width / 2 - 6,
                  customOnChanged: (value) => {
                    data.updatePenaltyField(
                        phaseIndex, penaltyIndex, penaltyType, "expand", value)
                  },
                )
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                BooleanSwitch(
                  initialValue: penalty.multiThread,
                  leftText: "Multithread",
                  width: width / 2 - 6,
                  customOnChanged: (value) => {
                    data.updatePenaltyField(phaseIndex, penaltyIndex,
                        penaltyType, "multi_thread", value)
                  },
                ),
                const SizedBox(width: 12),
                BooleanSwitch(
                  initialValue: penalty.derivative,
                  leftText: "Derivative",
                  width: width / 2 - 6,
                  customOnChanged: (value) => {
                    data.updatePenaltyField(phaseIndex, penaltyIndex,
                        penaltyType, "derivative", value)
                  },
                )
              ],
            ),
            Align(
              alignment: Alignment.centerRight,
              child: InkWell(
                onTap: () async {
                  final response = await _deletePenalties();
                  final newPenalties = (penaltyType == Constraint)
                      ? (json.decode(response.body) as List<dynamic>)
                          .map((c) => Constraint.fromJson(c))
                          .toList()
                      : (json.decode(response.body) as List<dynamic>)
                          .map((o) => Objective.fromJson(o))
                          .toList();
                  data.updatePenalties(phaseIndex, penaltyType, newPenalties);
                },
                borderRadius: BorderRadius.circular(25),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Remove ${_penaltyTypeToEndpoint(plural: false)}',
                        style: const TextStyle(color: Colors.red),
                      ),
                      const SizedBox(width: 8),
                      const Icon(
                        Icons.delete,
                        color: Colors.red,
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 14),
          ],
        ),
      );
    });
  }
}
