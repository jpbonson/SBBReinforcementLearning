import abc
import numpy
from collections import Counter, defaultdict
from ..utils.helpers import round_value, flatten, round_array
from ..config import Config

class DefaultMetrics(object):

    __metaclass__  = abc.ABCMeta

    def __init__(self, environment):
        self.environment_ = environment

    @abc.abstractmethod
    def metrics_for_team(self, team):
        """
        Generate a string with the metrics for the team specific of the environment.
        """

    @abc.abstractmethod
    def initialize_attributes_for_run_info(self, run_info):
        """
        Initialize the attributes in run_info, that will be the output at the end of the run.
        """

    @abc.abstractmethod
    def generate_output_for_attributes_for_run_info(self, run_info):
        """
        Generate an output of the attributes in run_info, to append it to the other results of the run.
        """

    @abc.abstractmethod
    def quick_metrics(self):
        """
        Generate a string with the metrics for the environment. It is printed at the 
        start and at the end of the execution, and it is also saved in the output file.
        """    

    def store_per_generation_metrics(self, run_info, teams_population, current_generation, previous_diversity):
        older_teams = [team for team in teams_population if team.generation != current_generation]
        mean_fitness = round_value(numpy.mean([team.fitness_ for team in older_teams]), 3)

        run_info.global_mean_fitness_per_generation_.append(mean_fitness)
        run_info.global_max_fitness_per_generation_.append(round_value(max([team.fitness_ for team in older_teams])))
        
        for diversity in Config.USER['advanced_training_parameters']['diversity']['metrics']:
            run_info.global_diversity_per_generation_[diversity].append(round_value(numpy.mean([t.diversity_[diversity] for t in older_teams]), 3))
        if len(Config.USER['advanced_training_parameters']['diversity']['metrics']) > 1 and previous_diversity:
            run_info.global_fitness_per_diversity_per_generation_[previous_diversity].append(mean_fitness)
            run_info.novelty_type_per_generation_.append(Config.USER['advanced_training_parameters']['diversity']['metrics'].index(previous_diversity))

    def store_per_validation_metrics(self, run_info, best_team, teams_population, programs_population, current_generation):
        run_info.train_score_per_validation_.append(best_team.fitness_)
        run_info.champion_score_per_validation_.append(best_team.score_champion_)
        
        older_teams = [team for team in teams_population if team.generation != current_generation]
        run_info.temp_info_['fitness_score_mean'] = round_value(numpy.mean([team.fitness_ for team in older_teams]))
        run_info.temp_info_['fitness_score_std'] = round_value(numpy.std([team.fitness_ for team in older_teams]))
        
        for key in best_team.diversity_:
            run_info.global_diversity_per_validation_[key].append(run_info.global_diversity_per_generation_[key][-1])

        actions_distribution = Counter([p.action for p in programs_population])
        actions_distribution_array = []
        for action in range(Config.RESTRICTIONS['total_actions']):
            if action in actions_distribution:
                actions_distribution_array.append(actions_distribution[action])
            else:
                actions_distribution_array.append(0)
        run_info.actions_distribution_per_validation_.append(actions_distribution_array)
        run_info.temp_info_['actions_distribution'] = actions_distribution

        inputs_distribution_per_instruction = Counter()
        inputs_distribution_per_team = Counter()
        for team in older_teams:
            inputs_distribution_per_instruction.update(team.inputs_distribution())
            inputs_distribution_per_team.update(list(team.inputs_distribution()))
        inputs_distribution_per_instruction_array = []
        inputs_distribution_per_team_array = []
        for value in range(Config.RESTRICTIONS['total_inputs']):
            if value in inputs_distribution_per_instruction:
                inputs_distribution_per_instruction_array.append(inputs_distribution_per_instruction[value])
            else:
                inputs_distribution_per_instruction_array.append(0)
            if value in inputs_distribution_per_team:
                inputs_distribution_per_team_array.append(inputs_distribution_per_team[value])
            else:
                inputs_distribution_per_team_array.append(0)
        run_info.inputs_distribution_per_instruction_per_validation_.append(inputs_distribution_per_instruction_array)
        run_info.inputs_distribution_per_team_per_validation_.append(inputs_distribution_per_team_array)
        run_info.temp_info_['inputs_distribution_per_instruction_array'] = inputs_distribution_per_instruction_array
        run_info.temp_info_['inputs_distribution_per_team_array'] = inputs_distribution_per_team_array
           
        avg_team_size = round_value(numpy.mean([len(team.programs) for team in older_teams]))
        avg_program_with_intros_size = round_value(numpy.mean(flatten([[len(program.instructions) for program in team.programs] for team in older_teams])))
        avg_program_without_intros_size = round_value(numpy.mean(flatten([[len(program.instructions_without_introns_) for program in team.programs] for team in older_teams])))
        run_info.mean_team_size_per_validation_.append(avg_team_size)
        run_info.mean_program_size_with_introns_per_validation_.append(avg_program_with_intros_size)
        run_info.mean_program_size_without_introns_per_validation_.append(avg_program_without_intros_size)

    def print_per_validation_metrics(self, run_info, best_team):
        print "\n### Champion Metrics: "+best_team.quick_metrics()+"\n"

        print "\n### Global Metrics:"
        
        for key in best_team.diversity_:
            print str(key)+": "+str(best_team.diversity_[key])+" (global: "+str(run_info.global_diversity_per_generation_[key][-1])+")"

        print ("\nfitness, mean (global): "+str(run_info.temp_info_['fitness_score_mean'])+""
            " (std: "+str(run_info.temp_info_['fitness_score_std']))+")"

        print "\nactions distribution: "+str(run_info.temp_info_['actions_distribution'])

        print "inputs distribution (global, per program): "+str(run_info.temp_info_['inputs_distribution_per_instruction_array'])
        print "inputs distribution (global, per team): "+str(run_info.temp_info_['inputs_distribution_per_team_array'])

        print
        print "Global Fitness (last 10 gen.): "+str(run_info.global_mean_fitness_per_generation_[-10:])
               
        if len(Config.USER['advanced_training_parameters']['diversity']['metrics']) > 0:
            print "Global Diversity (last 10 gen.):"
            for diversity in Config.USER['advanced_training_parameters']['diversity']['metrics']:
                print "- "+str(diversity)+": "+str(run_info.global_diversity_per_generation_[diversity][-10:])
        if len(Config.USER['advanced_training_parameters']['diversity']['metrics']) > 1:
            print "Diversity Type (last 10 gen.): "+str(run_info.novelty_type_per_generation_[-10:])
           
        print "\nMean Team Sizes: "+str(run_info.mean_team_size_per_validation_[-10:])
        print "Mean Program Sizes (with introns): "+str(run_info.mean_program_size_with_introns_per_validation_[-10:])
        print "Mean Program Sizes (without introns): "+str(run_info.mean_program_size_without_introns_per_validation_[-10:])

    def store_per_run_metrics(self, run_info, best_team, teams_population, pareto_front, current_generation):
        run_info.best_team_ = best_team
        for team in teams_population:
            if team.generation != current_generation:
                run_info.teams_in_last_generation_.append(team)
        run_info.pareto_front_in_last_generation_ = pareto_front
        run_info.hall_of_fame_in_last_generation_ = self.environment_.hall_of_fame()

    def generate_overall_metrics_output(self, run_infos):       
        msg = "\n\n\n#################### OVERALL RESULTS ####################"

        score_means, score_stds = self._process_scores([run.global_mean_fitness_per_generation_ for run in run_infos])
        msg += "\n\nGlobal Mean Fitness Score per Training:"
        msg += "\nmean: "+str(round_array(score_means, 3))
        if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
            msg += "\nstd. deviation: "+str(round_array(score_stds, 3))

        score_means, score_stds = self._process_scores([run.global_max_fitness_per_generation_ for run in run_infos])
        msg += "\n\nGlobal Max. Fitness Score per Training:"
        msg += "\nmean: "+str(round_array(score_means, 3))
        if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
            msg += "\nstd. deviation: "+str(round_array(score_stds, 3))

        score_means, score_stds = self._process_scores([run.champion_score_per_validation_ for run in run_infos])
        msg += "\n\nChampion Score per Validation:"
        msg += "\nmean: "+str(score_means)
        if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
            msg += "\nstd. deviation: "+str(score_stds)

        msg += "\n\nGlobal Diversities per Validation:"
        for key in Config.USER['advanced_training_parameters']['diversity']['metrics']:
            score_means, score_stds = self._process_scores([run.global_diversity_per_validation_[key] for run in run_infos])
            msg += "\n- "+str(key)+":"
            msg += "\n- mean: "+str(score_means)
            if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
                msg += "\n- std. deviation: "+str(score_stds)

        if not Config.USER['advanced_training_parameters']['second_layer']['enabled']:
            score_means, score_stds = self._process_scores([run.actions_distribution_per_validation_[-1] for run in run_infos])
            msg += "\n\nDistribution of Actions per Validation (last gen.):"
            msg += "\nmean: "+str(round_array(score_means, 2))
            if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
                msg += "\nstd. deviation: "+str(round_array(score_stds, 2))

        score_means, score_stds = self._process_scores([run.inputs_distribution_per_instruction_per_validation_[-1] for run in run_infos])
        msg += "\nDistribution of Inputs per Validation (per program) (last gen.):"
        msg += "\nmean: "+str(round_array(score_means, 2))
        if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
            msg += "\nstd. deviation: "+str(round_array(score_stds, 2))
        score_means, score_stds = self._process_scores([run.inputs_distribution_per_team_per_validation_[-1] for run in run_infos])
        msg += "\nDistribution of Inputs per Validation (per team) (last gen.):"
        msg += "\nmean: "+str(round_array(score_means, 2))
        if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
            msg += "\nstd. deviation: "+str(round_array(score_stds, 2))

        msg += "\n\nMean Team Sizes (last gen.): "+str(numpy.mean([run.mean_team_size_per_validation_[-1] for run in run_infos]))
        msg += "\nMean Program Sizes (with introns) (last gen.): "+str(numpy.mean([run.mean_program_size_with_introns_per_validation_[-1] for run in run_infos]))
        msg += "\nMean Program Sizes (without introns) (last gen.): "+str(numpy.mean([run.mean_program_size_without_introns_per_validation_[-1] for run in run_infos]))
        
        return msg

    def _process_scores(self, score_per_generation_per_run):
        score_means = []
        score_stds = []
        for index in range(len(score_per_generation_per_run[0])):
            column = [row[index] for row in score_per_generation_per_run]
            score_means.append(round_value(numpy.mean(column)))
            score_stds.append(round_value(numpy.std(column)))
        return score_means, score_stds

    def _generate_overall_metrics_output_for_acc_curves(self, run_infos):
        msg = ""
        metric = "score"
        msg += "\nOverall Accumulative Results ("+str(metric)+"):"
        score_means, score_stds = self._process_scores([run.individual_performance_in_last_generation_[metric] for run in run_infos])
        msg += "\n- Individual Team Performance:"
        msg += "\nmean: "+str(round_array(score_means, 3))
        if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
            msg += "\nstd. deviation: "+str(round_array(score_stds, 3))
        score_means, score_stds = self._process_scores([run.accumulative_performance_in_last_generation_[metric] for run in run_infos])
        msg += "\n- Accumulative Team Performance:"
        msg += "\nmean: "+str(round_array(score_means, 3))
        if not Config.USER['verbose']['dont_show_std_deviation_in_reports']:
            msg += "\nstd. deviation: "+str(round_array(score_stds, 3))
        msg += "\n\nAccumulative Results per Run ("+str(metric)+"):"
        msg += "\nindividual_values = ["
        for run in run_infos:
            msg += "\n"+str(run.individual_performance_in_last_generation_[metric])+","
        msg += "\n]"
        msg += "\nacc_values = ["
        for run in run_infos:
            msg += "\n"+str(run.accumulative_performance_in_last_generation_[metric])+","
        msg += "\n]"
        return msg