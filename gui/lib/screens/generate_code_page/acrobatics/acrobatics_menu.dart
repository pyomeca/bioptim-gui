import 'package:bioptim_gui/models/acrobatics_data.dart';
import 'package:bioptim_gui/models/acrobatics_request_maker.dart';
import 'package:bioptim_gui/models/ocp_data.dart';
import 'package:bioptim_gui/screens/generate_code_page/acrobatics/generate_acrobatics_phases.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_bio_model_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_information.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_position_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_sport_type_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatic_twist_side_chooser.dart';
import 'package:bioptim_gui/widgets/acrobatics/acrobatics_dynamics_chooser.dart';
import 'package:bioptim_gui/widgets/utils/animated_expanding_widget.dart';
import 'package:bioptim_gui/widgets/utils/extensions.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class AcrobaticsMenu extends StatefulWidget {
  const AcrobaticsMenu({super.key, this.columnWidth = 500.0});

  final double columnWidth;

  @override
  State<AcrobaticsMenu> createState() => _AcrobaticsMenuState();
}

class _AcrobaticsMenuState extends State<AcrobaticsMenu> {
  final _verticalScroll = ScrollController();

  AcrobaticsData? _data;

  @override
  void dispose() {
    _verticalScroll.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  Future<void> fetchData() async {
    final data = await AcrobaticsRequestMaker().fetchData();
    setState(() {
      _data = data;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_data == null) {
      return const CircularProgressIndicator();
    } else {
      return ChangeNotifierProvider<OCPData>(
        create: (context) => _data!,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            _HeaderBuilder(width: widget.columnWidth),
            const SizedBox(height: 12),
            const Divider(),
            const SizedBox(height: 12),
            _PhaseBuilder(
              width: widget.columnWidth,
            ),
          ],
        ),
      );
    }
  }
}

class _HeaderBuilder extends StatelessWidget {
  const _HeaderBuilder({
    required this.width,
  });

  final double width;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: SizedBox(
        width: width,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 12),
            Consumer<OCPData>(builder: (context, data, child) {
              final acrobaticsData = data as AcrobaticsData;
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(children: [
                    AcrobaticSportTypeChooser(
                        width: width * 0.35 - 6,
                        defaultValue: acrobaticsData.sportType.capitalize()),
                    const SizedBox(width: 12),
                    AcrobaticsDynamicChooser(width: width * 0.65 - 6),
                  ]),
                  const SizedBox(height: 12),
                  AcrobaticBioModelChooser(
                    width: width,
                    defaultValue: acrobaticsData.modelPath,
                  ),
                  const SizedBox(height: 12),
                  AcrobaticInformation(width: width),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      SizedBox(
                          width: width / 2 - 6,
                          child: AcrobaticTwistSideChooser(
                            width: width,
                            defaultValue:
                                acrobaticsData.preferredTwistSide.capitalize(),
                          )),
                      const SizedBox(width: 12),
                      SizedBox(
                          width: width / 2 - 6,
                          child: AcrobaticPositionChooser(
                            width: width,
                            defaultValue: acrobaticsData.position.capitalize(),
                          )),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // list acrobaticsData.dofNames
                  AnimatedExpandingWidget(
                    header: SizedBox(
                      width: width,
                      child: const Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          "Degrees of freedom",
                          style: TextStyle(
                              fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                    child: SizedBox(
                      width: width,
                      height: 25.0 * acrobaticsData.dofNames.length.toDouble(),
                      child: ListView.builder(
                        controller: ScrollController(),
                        scrollDirection: Axis.vertical,
                        itemCount: acrobaticsData.dofNames.length,
                        itemBuilder: (context, index) {
                          return SizedBox(
                            width: 100,
                            child: Text(
                              '$index ${acrobaticsData.dofNames[index]}',
                              style: const TextStyle(fontSize: 16),
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                ],
              );
            }),
          ],
        ),
      ),
    );
  }
}

class _PhaseBuilder extends StatefulWidget {
  const _PhaseBuilder({
    required this.width,
  });

  final double width;

  @override
  State<_PhaseBuilder> createState() => _PhaseBuilderState();
}

class _PhaseBuilderState extends State<_PhaseBuilder> {
  final _horizontalScroll = ScrollController();

  @override
  void dispose() {
    _horizontalScroll.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RawScrollbar(
      controller: _horizontalScroll,
      thumbVisibility: true,
      thumbColor: Theme.of(context).colorScheme.secondary,
      thickness: 8,
      radius: const Radius.circular(25),
      child: SingleChildScrollView(
        controller: _horizontalScroll,
        scrollDirection: Axis.horizontal,
        child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SomersaultGenerationMenu(
                width: widget.width,
              ),
            ]),
      ),
    );
  }
}
