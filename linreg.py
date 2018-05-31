# export PYTHONPATH=./ 
# luigi --module linreg LinRegAllDatasets --scheduler-host luigi-service.default --workers 4


import luigi
from luigi.contrib.kubernetes import KubernetesJobTask
from os.path import basename
import glob
from datetime import datetime

class LinRegTask(KubernetesJobTask):
    
    datasetFile = luigi.Parameter()
    t_start = datetime.now()
    name = "lin-reg"
    max_retrials = 1
    
    @property
    def spec_schema(self): 
        return {
            "automountServiceAccountToken": "false",
            "containers": [{
                "name": self.name,
                "image": "nsadawi/lin-reg",
                "args": [
                    self.datasetFile,
                ],
                "resources": {
                  "requests": {
                    "memory": "2G",
                    "cpu": "1"
                  }
                },
                "volumeMounts": [{
                    "mountPath": "/work",#inside the lin-reg container
                    "name": "shared-volume",
                    "subPath": "jupyter/LinReg"#in host .. i.e. where we run this script
                 }]
             }],
             "volumes": [{
                 "name": "shared-volume",
                 "persistentVolumeClaim": {
                     "claimName": "galaxy-pvc"
                 }
             }]
        }
    
    def output(self):
        filename = self.datasetFile + ".out"
        t_end = datetime.now()
        print(">>>>>> " + filename + " -> "+ str(t_end-self.t_start) +" <<<<<<")
        ### filename = "data/results.csv"
        return luigi.LocalTarget(filename)

class LinRegAllDatasets(luigi.WrapperTask):
    def requires(self):
        inputFiles = glob.glob("randomised-datasets/*.csv")
        for inputFile in inputFiles:
            yield LinRegTask(datasetFile=inputFile)
