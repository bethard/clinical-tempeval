import logging
import os.path
import sys
import anafora.evaluate

[_, input_dir, output_dir] = sys.argv

reference_dir = os.path.join(input_dir, 'ref')
predicted_dir = os.path.join(input_dir, 'res')

subdir_diff = set(os.listdir(reference_dir)) - set(os.listdir(predicted_dir))
if subdir_diff:
    logging.warning("predictions not found for {0}".format(subdir_diff))

event_time_scores = anafora.evaluate.score_dirs(
    reference_dir=reference_dir,
    predicted_dir=predicted_dir,
    xml_name_regex=".*[.]Temporal.*[.]xml",
    include=["TIMEX3", "EVENT"],
    exclude=[("TIMEX3", "*", "*"), ("EVENT", "*", "*"),
             ("EVENT", "ContextualAspect"), ("EVENT", "Permanence")])

tlink_scores = anafora.evaluate.score_dirs(
    reference_dir=reference_dir,
    predicted_dir=predicted_dir,
    xml_name_regex="(?i).*clin.*[.]Temporal.*[.]xml",
    include=[("TLINK", "Type", "CONTAINS")],
    scores_type=anafora.evaluate.TemporalClosureScores)

all_named_scores = {}
for file_named_scores, get_dict in [(event_time_scores, anafora.evaluate.Scores),
                                    (tlink_scores, anafora.evaluate.TemporalClosureScores)]:
    for _, named_scores in file_named_scores:
        for name, scores in named_scores.items():
            name = "_".join(name) if isinstance(name, tuple) else name
            name = name.replace('*', 'ALL').replace('<span>', 'SPAN')
            if name not in all_named_scores:
                all_named_scores[name] = get_dict()
            all_named_scores[name].update(scores)
    
with open(os.path.join(output_dir, "scores.txt"), "w") as scores_file:    
    for name, scores in sorted(all_named_scores.items()):
        for score_name in ["precision", "recall", "f1"]:
            score = getattr(scores, score_name)()
            scores_file.write('{0}_{1}: {2}\n'.format(
                name, score_name, score))
