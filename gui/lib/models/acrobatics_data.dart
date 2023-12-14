import 'dart:convert';
import 'dart:math';

import 'package:bioptim_gui/models/acrobatics_controllers.dart';
import 'package:bioptim_gui/models/acrobatics_request_maker.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/models/penalty.dart';
import 'package:flutter/foundation.dart';

class AcrobaticsData extends ChangeNotifier implements OCPData {
  int _nbSomersaults;
  List<int> halfTwists = [];
  String _modelPath;
  double finalTime;
  double finalTimeMargin;
  String position;
  String sportType;
  String preferredTwistSide;
  bool withVisualCriteria;
  bool collisionConstraint;
  bool withSpine;
  String dynamics;
  List<SomersaultPhase> _phasesInfo = [];

  AcrobaticsData.fromJson(Map<String, dynamic> data)
      : _nbSomersaults = data["nb_somersaults"],
        halfTwists = List.from(data["nb_half_twists"]),
        _modelPath = data["model_path"],
        finalTime = data["final_time"],
        finalTimeMargin = data["final_time_margin"],
        position = data["position"],
        sportType = data["sport_type"],
        preferredTwistSide = data["preferred_twist_side"],
        withVisualCriteria = data["with_visual_criteria"],
        collisionConstraint = data["collision_constraint"],
        withSpine = data["with_spine"],
        dynamics = data["dynamics"],
        _phasesInfo = (data["phases_info"] as List<dynamic>).map((somersault) {
          return SomersaultPhase.fromJson(somersault);
        }).toList();

  ///
  /// Getters Setters

  @override
  AcrobaticsRequestMaker get requestMaker {
    return AcrobaticsRequestMaker();
  }

  @override
  List<Phase> get phaseInfo => _phasesInfo;

  @override
  String get modelPath => _modelPath;

  @override
  int get nbPhases => phaseInfo.length;

  int get nbSomersaults => _nbSomersaults;
  set nbSomersaults(int value) {
    _nbSomersaults = value;
    notifyListeners();
  }

  ///
  /// Update methods

  void updateHalfTwists(int index, int value) async {
    final response = await requestMaker.updateHalfTwists(index, value);

    final newPhases = (json.decode(response.body) as List<dynamic>)
        .map((p) => SomersaultPhase.fromJson(p))
        .toList();

    _phasesInfo = newPhases;

    halfTwists[index] = value;
    notifyListeners();
  }

  void updateDynamics(String value) async {
    final response = await requestMaker.updateField("dynamics", value);

    final newPhases = (json.decode(response.body) as List<dynamic>)
        .map((p) => SomersaultPhase.fromJson(p))
        .toList();

    _phasesInfo = newPhases;
    dynamics = value;
    notifyListeners();
  }

  Future<bool> updatePosition(String value) async {
    final response = await requestMaker.updateField("position", value);

    if (response.statusCode != 200) {
      return Future(() => false);
    }

    final newData = AcrobaticsData.fromJson(json.decode(response.body));

    updateData(newData);
    return Future(() => true);
  }

  @override
  void updateField(String name, String value) {
    requestMaker.updateField(name, value);

    switch (name) {
      case "nb_somersaults":
        nbSomersaults = int.parse(value);
        break;
      case "model_path":
        _modelPath = value;
        break;
      case "final_time":
        finalTime = double.parse(value);
        break;
      case "final_time_margin":
        finalTimeMargin = double.parse(value);
        break;
      case "position":
        position = value;
        break;
      case "sport_type":
        sportType = value;
        break;
      case "preferred_twist_side":
        preferredTwistSide = value;
        break;
      case "with_visual_criteria":
        withVisualCriteria = value == "true";
        break;
      case "collision_constraint":
        collisionConstraint = value == "true";
        break;
      case "with_spine":
        withSpine = value == "true";
        break;
      case "dynamics":
        dynamics = value;
        break;
      default:
        break;
    }
    notifyListeners();
  }

  @override
  void updatePhaseField(int phaseIndex, String fieldName, String newValue) {
    requestMaker.updatePhaseField(phaseIndex, fieldName, newValue);

    switch (fieldName) {
      case "duration":
        _phasesInfo[phaseIndex].duration = double.parse(newValue);
        break;
      case "nb_shooting_points":
        _phasesInfo[phaseIndex].nbShootingPoints = int.parse(newValue);
        break;
      default:
        break;
    }
    notifyListeners();
  }

  void updateData(AcrobaticsData newData) {
    nbSomersaults = newData.nbSomersaults;
    halfTwists = List.from(newData.halfTwists);
    _modelPath = newData._modelPath;
    finalTime = newData.finalTime;
    finalTimeMargin = newData.finalTimeMargin;
    position = newData.position;
    sportType = newData.sportType;
    preferredTwistSide = newData.preferredTwistSide;
    withVisualCriteria = newData.withVisualCriteria;
    collisionConstraint = newData.collisionConstraint;
    withSpine = newData.withSpine;
    dynamics = newData.dynamics;
    _phasesInfo = List.from(newData._phasesInfo);

    notifyListeners();
  }

  @override
  void updatePenalties(
      int somersaultIndex, String penaltyType, List<Penalty> penalties) {
    if (penaltyType == "objective") {
      _phasesInfo[somersaultIndex].objectives = penalties as List<Objective>;
    } else {
      _phasesInfo[somersaultIndex].constraints = penalties as List<Constraint>;
    }
    notifyListeners();
  }

  @override
  void updatePenalty(int somersaultIndex, String penaltyType, int penaltyIndex,
      Penalty penalty) {
    final oldPenalty = penaltyType == "objective"
        ? _phasesInfo[somersaultIndex].objectives[penaltyIndex]
        : _phasesInfo[somersaultIndex].constraints[penaltyIndex];

    final newPenaltyType = penalty.penaltyType;
    final oldPenaltyType = oldPenalty.penaltyType;
    final penaltyTypeChanged = newPenaltyType != oldPenaltyType;

    final objectiveTypeChanged = penaltyType == "objective"
        ? (penalty as Objective).objectiveType !=
            (oldPenalty as Objective).objectiveType
        : false;

    final minMaxChanged = penaltyType == "objective"
        ? (penalty as Objective).weight * (oldPenalty as Objective).weight > 0
        : false;

    // keep expanded value
    penalty.expanded =
        _phasesInfo[somersaultIndex].objectives[penaltyIndex].expanded;

    if (penaltyType == "objective") {
      _phasesInfo[somersaultIndex].objectives[penaltyIndex] =
          penalty as Objective;
    } else {
      _phasesInfo[somersaultIndex].constraints[penaltyIndex] =
          penalty as Constraint;
    }

    // force redraw only if the penalty type or objective type if it's an objective
    // changes (to update arguments)
    if (penaltyTypeChanged || objectiveTypeChanged || minMaxChanged) {
      notifyListeners();
    }
  }

  @override
  void updatePhaseInfo(List newData) {
    final newPhases =
        (newData).map((p) => SomersaultPhase.fromJson(p)).toList();

    _phasesInfo = newPhases;

    notifyListeners();
  }

  @override
  void notifyListeners() {
    AcrobaticsControllers.instance.notifyListeners();
    super.notifyListeners();
  }

  @override
  void updatePenaltyArgument(
      int phaseIndex,
      int objectiveIndex,
      String argumentName,
      String? newValue,
      String argumentType,
      int argumentIndex,
      String penaltyType) {
    requestMaker.updatePenaltyArgument(phaseIndex, objectiveIndex, argumentName,
        newValue, argumentType, penaltyType);

    _phasesInfo[phaseIndex]
        .objectives[objectiveIndex]
        .arguments[argumentIndex]
        .value = newValue;

    notifyListeners();
  }

  @override
  Future<bool> updatePenaltyField(int phaseIndex, int penaltyIndex,
      String penaltyType, String fieldName, dynamic newValue,
      {bool? doUpdate}) async {
    final response = await requestMaker.updatePenaltyField(
        phaseIndex, penaltyType, penaltyIndex, fieldName, newValue);

    if (response.statusCode != 200) {
      return Future(() => false);
    }

    final isObjective = penaltyType == "objectives";

    switch (fieldName) {
      case "target":
        _phasesInfo[phaseIndex].objectives[penaltyIndex].target = newValue;
        break;
      case "integration_rule":
        _phasesInfo[phaseIndex].objectives[penaltyIndex].integrationRule =
            newValue!;
        break;
      case "weight":
        _phasesInfo[phaseIndex].objectives[penaltyIndex].weight =
            double.tryParse(newValue!) ?? 0.0;
        break;
      case "nodes":
        _phasesInfo[phaseIndex].constraints[penaltyIndex].nodes = newValue!;
        break;
      case "quadratic":
        _phasesInfo[phaseIndex].constraints[penaltyIndex].quadratic =
            newValue == "true";
        break;
      case "expand":
        _phasesInfo[phaseIndex].constraints[penaltyIndex].expand =
            newValue == "true";
        break;
      case "multi_thread":
        _phasesInfo[phaseIndex].constraints[penaltyIndex].multiThread =
            newValue == "true";
        break;
      case "derivative":
        _phasesInfo[phaseIndex].constraints[penaltyIndex].derivative =
            newValue == "true";
        break;
      default:
        break;
    }

    if (doUpdate != null && doUpdate) {
      final Penalty newPenalties = isObjective
          ? Objective.fromJson(
              json.decode(response.body) as Map<String, dynamic>)
          : Constraint.fromJson(
              json.decode(response.body) as Map<String, dynamic>);

      newPenalties.expand = _phasesInfo[phaseIndex]
          .objectives[penaltyIndex]
          .expanded; // keep expanded value

      if (isObjective) {
        updatePenalty(phaseIndex, "objective", penaltyIndex, newPenalties);
      } else {
        updatePenalty(phaseIndex, "constraint", penaltyIndex, newPenalties);
      }
    } else {
      notifyListeners();
    }

    return Future(() => true);
  }
}

class SomersaultPhase extends Phase {
  SomersaultPhase.fromJson(Map<String, dynamic> somersaultData)
      : super.fromJson(somersaultData);
}
