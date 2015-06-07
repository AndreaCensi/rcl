from aer.programs.stats_freq.meat import aer_stats_freq_meat

from quickapp import QuickApp
from quickapp.app_utils.subcontexts import iterate_context_names


class AERStatsFreqApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("log", help='source file')
                            
    def define_jobs_context(self, context):
        options = self.get_options()
        pipelines = ['p2n', 'n2p', 'both']
        for c, pipeline in iterate_context_names(context, pipelines):
            c.add_extra_report_keys(pipeline=pipeline)

            r = c.comp(aer_stats_freq_meat, options.log, pipeline)
            c.add_report(r, 'rep1')
 

aer_stats_freq_main = AERStatsFreqApp.get_sys_main()

