# make sure you setup the pythonpath
# export PYTHONPATH=./ 
# this is how you run several workers in parallel
# time luigi --module linreg LinRegAllDatasets --scheduler-host luigi-service.default --workers 100

import luigi
from luigi.contrib.kubernetes import KubernetesJobTask
import glob
  
class LinRegTask(KubernetesJobTask):
    # dataset file as a luigi paramter 
    datasetFile = luigi.Parameter()
    name = "lin-reg" # give the task a name 
    max_retrials = 1 # how many times to retry it it fails 
    
    @property
    def spec_schema(self): 
        return { # container specifications 
            "containers": [{
                "name": self.name,
                "image": "nsadawi/lin-reg",# container on docker hub
                "args": [# the input file we pass as an argument
                    self.datasetFile,
                ],
                # resources allocated to each task
                "resources": {
                  "requests": {
                    "memory": "1G",
                    "cpu": "1"
                  },# do not exceed these limits
                  "limits": {
                    "memory": "1G",
                    "cpu": "1"
                  }
                },
                # specifications of volume mounts
                "volumeMounts": [{
                    "mountPath": "/work", # inside the container
                    "name": "shared-volume",
                    "subPath": "jupyter/LinReg" # on host .. i.e. where we run this script
                 }]
             }],
             # volume name and specifications under PhenoMeNal
             "volumes": [{
                 "name": "shared-volume",
                 "persistentVolumeClaim": {
                     "claimName": "galaxy-pvc"
                 }
             }]
        }
    
    # this tells luigi the task is finished when this file is created
    def output(self):
        filename = self.datasetFile + ".out"
        return luigi.LocalTarget(filename)

# here we loop through all csv files and create a task for each one
class LinRegAllDatasets(luigi.WrapperTask):
    def requires(self):
        inputFiles = glob.glob("randomised-datasets/*.csv")
        for inputFile in inputFiles:
            yield LinRegTask(datasetFile=inputFile)