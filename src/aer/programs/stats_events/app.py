from quickapp import QuickApp
from .meat import aer_stats_events_meat


__all__ = ['aer_stats_events_main']


class AERStatsEventsApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("log", help='source file')
       
    def define_jobs_context(self, context):
        options = self.get_options()
        report = context.comp(aer_stats_events_meat, options.log)
        context.add_report(report, 'rep1')
 
aer_stats_events_main = AERStatsEventsApp.get_sys_main()

    
