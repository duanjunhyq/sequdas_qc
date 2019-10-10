import os
import subprocess
import shutil
import re
import json
import csv
import time
from sequdas_qc.Lib.core import * 
from subprocess import Popen
exe_path = os.path.abspath(os.path.dirname(sys.argv[0]))
def run_machine_QC(directory,out_dir):
    print(directory)
    command_list1=["interop_plot_by_cycle","interop_plot_by_lane","interop_plot_flowcell","interop_plot_qscore_histogram","interop_plot_qscore_heatmap","interop_plot_sample_qc"]
    command_list2=["interop_summary","interop_index-summary"]
    filetype_list=["_ClusterCount-by-lane.png","_flowcell-Intensity.png","_Intensity-by-cycle_Intensity.png","_q-heat-map.png","_q-histogram.png","_sample-qc.png"]
    run_folder_name=os.path.basename(os.path.normpath(directory))
    run_analysis_folder=out_dir+"/"+run_folder_name
    samplesheet_file=directory+"/"+"SampleSheet.csv"
    print(samplesheet_file)
    shutil.copy(samplesheet_file,run_analysis_folder)
    subprocess.call(['chmod', '755', run_analysis_folder+"/"+"SampleSheet.csv"])
    for command in command_list1:
        filename_output=run_analysis_folder+"/"+run_folder_name+"_"+command+".csv"
        try: 
            with open(filename_output, 'w') as output_file:
                p1 = subprocess.Popen([command,directory],stdout=output_file)
            output_file.close()
            a=p1.wait()            
            if(a==0):
                try:
                    plot_command='gnuplot '+filename_output
                    run_plot = subprocess.Popen(plot_command,shell=True,stdout=subprocess.PIPE,)
                except:
                    print("Error, please check gnuplot!")                            
        except:
            print("Errors, please check "+command)
    for command in command_list2:
        filename_output=run_analysis_folder+"/"+run_folder_name+"_"+command+".txt"
        try: 
            with open(filename_output, 'w') as output_file:
                p1 = subprocess.Popen([command,directory],stdout=output_file)
            output_file.close()
            a=p1.wait()                              
        except:
            print("Errors, please check "+command) 

    try:######################################################### Create density file
        summary_file=run_analysis_folder+"/"+run_folder_name+"_"+"interop_summary.txt"
        with open(run_analysis_folder+"/"+run_folder_name+"_"+'density.txt', 'w') as outfile: 
            json.dump(get_mean(create_dict(summary_file)), outfile)
    except: 
        print("Errors, please check summary")

    for extention in filetype_list:
        src=run_folder_name+extention
        try:
           shutil.move(src,run_analysis_folder)
        except:
           os.remove(src)


def run_fastqc(directory,out_dir, server_dir):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    run_analysis_folder=out_dir+"/"+run_folder_name
    fastq_files = os.listdir(fastq_file_location)
    for fastq_file in fastq_files:
        if fastq_file.endswith(".fastq.gz"):
           p1 = subprocess.call(['fastqc' ,fastq_file_location+fastq_file])
    fastqc_results = os.listdir(fastq_file_location)
    for fastqc_result in fastqc_results:
        matchObj = re.match( r'(.*)\_S\d+\_L\d{3}\_(R\d+)\_\S+(_fastqc.html)', fastqc_result, re.M|re.I)
        if matchObj:
            if(matchObj.group(2)=="R1"):
                shutil.copy2(fastq_file_location+"/"+fastqc_result, run_analysis_folder+"/"+matchObj.group(1)+"_F.html")                  
            if(matchObj.group(2)=="R2"):
                shutil.copy2(fastq_file_location+"/"+fastqc_result, run_analysis_folder+"/"+matchObj.group(1)+"_R.html")   
    try:######################################################### Create coverage file
        with open(run_analysis_folder+"/"+run_folder_name+"_"+'coverage.txt', 'w') as outfile: 
            json.dump((create_sample_dict( directory)), outfile)
    except: 
        print("Errors, please check spreadsheet")


def run_fastqc_cluster(directory,out_dir,server_dir):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    run_analysis_folder=out_dir+"/"+run_folder_name
    run_analysis_folder=os.path.abspath(run_analysis_folder)
    fastq_files = os.listdir(fastq_file_location)
    log_dir=server_dir+"/Log/Qsub"
    for fastq_file in fastq_files:
        if fastq_file.endswith(".fastq.gz"):
            print("qsub "+server_dir+"/Lib/Cluster/fastqc.sh " + fastq_file_location+fastq_file+" "+server_dir+"/Lib/Cluster" +" -e "+log_dir+" -o "+log_dir)
            subprocess.call("qsub "+server_dir+"/Lib/Cluster/fastqc.sh " + fastq_file_location+fastq_file+" "+server_dir+"/Lib/Cluster" +" -e "+log_dir+" -o "+log_dir, shell = True)
    wait_until("sequdas_fastqc")
    # fastqc_results = os.listdir(fastq_file_location)
    # for fastqc_result in fastqc_results:
    #     matchObj = re.match( r'(.*)\_S\d+\_L\d{3}\_(R\d+)\_\S+(_fastqc.html)', fastqc_result, re.M|re.I)
    #     if matchObj:
    #         if(matchObj.group(2)=="R1"):
    #             shutil.copy2(fastq_file_location+"/"+fastqc_result, run_analysis_folder+"/"+matchObj.group(1)+"_F.html")                  
    #         if(matchObj.group(2)=="R2"):
    #             shutil.copy2(fastq_file_location+"/"+fastqc_result, run_analysis_folder+"/"+matchObj.group(1)+"_R.html")   
    # try:
    #     rough_list = read_data_csv(directory)
    #     sample_list = make_sample_list(rough_list)
    #     fastq_dictionary = make_fastq_dict(directory)
    #     for each_sample in sample_list:
    #         if len(sample_list) == 0:
    #             return "N/A"
    #         if isinstance(each_sample, basestring):
    #             fastq_file_location= directory+"/Data/Intensities/BaseCalls/"
    #             path_f = fastq_dictionary[each_sample + "_R1"]
    #             path_f = fastq_file_location + path_f
    #             path_r = fastq_dictionary[each_sample + "_R2"]
    #             path_r = fastq_file_location + path_r
    #             path_f = os.path.abspath(path_f)
    #             path_r = os.path.abspath(path_r)
    #             subprocess.call("qsub "+server_dir+"/Lib/Cluster/coverage.sh "+ path_f +" " + path_r +" " +run_analysis_folder + " " + run_folder_name + " " +each_sample+" "+server_dir, shell = True)
    #             print("qsub "+server_dir+"/Lib/Cluster/coverage.sh "+ path_f +" " + path_r +" " +run_analysis_folder + " " + run_folder_name + " " +each_sample+" "+server_dir)
    # except:
    #     print("There was an issue with the samplesheet, continuing...")
    # wait_until("sequdas_coverage")
    # with open(run_analysis_folder+"/"+run_folder_name+"_"+'interop_summary.txt', 'w') as outfile:
    #     json.dump(create_sample_dict_cluster(directory, run_analysis_folder, run_folder_name), outfile)
    
    # delete = del_list();
    # for each in delete:
    #     subprocess.call("rm " + each, shell = True)


def run_multiQC(directory,out_dir):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    multQC_result=run_folder_name+"_"+"qcreport"+".html"
    run_analysis_folder=out_dir+"/"+run_folder_name
    check_folder(run_analysis_folder)
    fastq_file_location=directory+"/Data/Intensities/BaseCalls"
    p2 = subprocess.call(['multiqc','-n',multQC_result,'-f',fastq_file_location,'-o',run_analysis_folder]) 


def run_kraken2(directory,out_dir,keep_kraken, db, krona, server_dir):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    run_analysis_folder=out_dir+"/"+run_folder_name
    sample_sheets=[directory+"/"+"SampleSheet.csv"]
    metadata=parse_metadata(sample_sheets[0])
    sample_list=parse_samples(sample_sheets[0])
    fastq_files = os.listdir(fastq_file_location)
    fastq_file_dict = {}
    for fastq_file in fastq_files:
        if fastq_file.endswith(".fastq.gz"):
            matchObj = re.match( r'(.*)\_S\d+\_L\d{3}\_(R\d+)\_\S+(fastq.gz)', fastq_file, re.M|re.I)
            if matchObj:
                if(matchObj.group(2)=="R1" or matchObj.group(2)=="R2"):
                    key=matchObj.group(1)+"_"+matchObj.group(2)
                    fastq_file_dict[key]=fastq_file
    for sample in sample_list:
        if(len(sample['sampleName'])==0 and len(sample['sequencerSampleId'])==0):
           continue     
        if(len(sample['sampleName'])>0):
            sample_name_t=sample['sampleName']
        else:
            sample_name_t=sample['sequencerSampleId']
        sample_name_t=sample_name_t.replace('_','-')
        sample_name_t=sample_name_t.replace(' ','-')
        sample_name_t=sample_name_t.replace('.','-')
        sample_name_t_R1=sample_name_t+"_R1";
        sample_name_t_R2=sample_name_t+"_R2";
        fq_F=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R1]
        fq_R=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R2]
        try:
           kraken_result_file=run_analysis_folder+"/"+sample_name_t+"_kraken2.out"
           kraken_report_file=run_analysis_folder+"/"+sample_name_t+"_kraken2_report.txt"
           statement = 'kraken2 --threads 10 --db '+db+' --report ' +kraken_report_file+ ' --output ' +kraken_result_file + ' --paired --gzip-compressed ' + fq_F +' ' +fq_R  
           subprocess.call([statement],shell=True)
           kraken_json_file=run_analysis_folder+"/"+sample_name_t+"_kraken2.js"
           with open(kraken_json_file, 'w') as output_file:
               p3_3=subprocess.call(['python',server_dir+'/kraken_parse.py','G','2','5',kraken_report_file],stdout=output_file)
           output_file.close()
           kraken_sorted_for_krona=run_analysis_folder+"/"+sample_name_t+"_kraken2_krona.ini"
           with open(kraken_sorted_for_krona, 'w') as output_file:
               p3_4=subprocess.call(['cut','-f2,3',kraken_result_file],stdout=output_file)
           output_file.close()
           krona_result_file=run_analysis_folder+"/"+sample_name_t+"_kraken2_krona.out.html"
           p3_5= subprocess.call([krona,kraken_sorted_for_krona,'-o', krona_result_file])
           if(keep_kraken is False):
               p3_6= subprocess.call(['rm','-fr', kraken_result_file])
               p3_7= subprocess.call(['rm','-fr', kraken_sorted_for_krona])
        except:     
           print("error,please check Kraken")
    try:
        cover(run_analysis_folder+"/", run_folder_name)
    except:
        print("No coverage file to check... proceeding...")
    print("complete")

def run_kraken2_cluster(directory,out_dir,keep_kraken, db, krona, server_dir):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    run_analysis_folder=out_dir+"/"+run_folder_name
    sample_sheets=[directory+"/"+"SampleSheet.csv"]
    metadata=parse_metadata(sample_sheets[0])
    sample_list=parse_samples(sample_sheets[0])
    fastq_files = os.listdir(fastq_file_location)
    fastq_file_dict = {}
    for fastq_file in fastq_files:
        if fastq_file.endswith(".fastq.gz"):
            matchObj = re.match( r'(.*)\_S\d+\_L\d{3}\_(R\d+)\_\S+(fastq.gz)', fastq_file, re.M|re.I)
            if matchObj:
                if(matchObj.group(2)=="R1" or matchObj.group(2)=="R2"):
                    key=matchObj.group(1)+"_"+matchObj.group(2)
                    fastq_file_dict[key]=fastq_file
    for sample in sample_list:
        if(len(sample['sampleName'])==0 and len(sample['sequencerSampleId'])==0):
           continue     
        if(len(sample['sampleName'])>0):
            sample_name_t=sample['sampleName']
        else:
            sample_name_t=sample['sequencerSampleId']
        sample_name_t=sample_name_t.replace('_','-')
        sample_name_t=sample_name_t.replace(' ','-')
        sample_name_t=sample_name_t.replace('.','-')
        sample_name_t_R1=sample_name_t+"_R1";
        sample_name_t_R2=sample_name_t+"_R2";
        fq_F=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R1]
        fq_R=directory+"/Data/Intensities/BaseCalls/"+fastq_file_dict[sample_name_t_R2]
        try:
           kraken_result_file=run_analysis_folder+"/"+sample_name_t+"_kraken2.out"
           kraken_report_file=run_analysis_folder+"/"+sample_name_t+"_kraken2_report.txt"
           subprocess.call("qsub "+server_dir+"/Lib/Cluster/kraken2.sh " +kraken_report_file + " " +kraken_result_file + " " + fq_F + " " + fq_R+" "+server_dir+"/Lib/Cluster"+" "+db, shell = True )
           #print("qsub "+server_dir+"/Lib/Cluster/kraken2.sh " +kraken_report_file + " " +kraken_result_file + " " + fq_F + " " + fq_R+" "+server_dir+"/Lib/Cluster"+" "+db)
        except:     
           print("error,please check Kraken")
    wait_until("sequdas_kraken2")
    for sample in sample_list:
        if(len(sample['sampleName'])==0 and len(sample['sequencerSampleId'])==0):
           continue     
        if(len(sample['sampleName'])>0):
            sample_name_t=sample['sampleName']
        else:
            sample_name_t=sample['sequencerSampleId']
        sample_name_t=sample_name_t.replace('_','-')
        sample_name_t=sample_name_t.replace(' ','-')
        sample_name_t=sample_name_t.replace('.','-')
        sample_name_t_R1=sample_name_t+"_R1";
        sample_name_t_R2=sample_name_t+"_R2";
        try:
           kraken_result_file=run_analysis_folder+"/"+sample_name_t+"_kraken2.out"
           kraken_report_file=run_analysis_folder+"/"+sample_name_t+"_kraken2_report.txt"
           kraken_json_file=run_analysis_folder+"/"+sample_name_t+"_kraken2.js"
           with open(kraken_json_file, 'w') as output_file:
               subprocess.call(['python',server_dir+'/kraken_parse.py','G','2','5',kraken_report_file],stdout=output_file)
           output_file.close()
           kraken_sorted_for_krona=run_analysis_folder+"/"+sample_name_t+"_kraken2_krona.ini"
           krona_result_file=run_analysis_folder+"/"+sample_name_t+"_kraken2_krona.out.html"
           #print("qsub "+server_dir+"/Lib/Cluster/krona.sh " +kraken_json_file+ " "+ kraken_report_file+ " "+ kraken_sorted_for_krona+ " "+ kraken_result_file+ " "+ krona_result_file +" "+server_dir+" "+krona)
           subprocess.call("qsub "+server_dir+"/Lib/Cluster/krona.sh " +kraken_json_file+ " "+ kraken_report_file+ " "+ kraken_sorted_for_krona+ " "+ kraken_result_file+ " "+ krona_result_file +" "+server_dir+" "+krona, shell = True)
        except:     
           print("error,please check Krona")
    wait_until("sequdas_krona")
    for sample in sample_list:
        if(len(sample['sampleName'])==0 and len(sample['sequencerSampleId'])==0):
           continue     
        if(len(sample['sampleName'])>0):
            sample_name_t=sample['sampleName']
        else:
            sample_name_t=sample['sequencerSampleId']
            sample_name_t=sample_name_t.replace('_','-')
            sample_name_t=sample_name_t.replace(' ','-')
            sample_name_t=sample_name_t.replace('.','-')
            sample_name_t_R1=sample_name_t+"_R1";
            sample_name_t_R2=sample_name_t+"_R2";
            kraken_result_file=run_analysis_folder+"/"+sample_name_t+"_kraken2.out"
            kraken_sorted_for_krona=run_analysis_folder+"/"+sample_name_t+"_kraken2_krona.ini"
            if(keep_kraken is False):
               p3_6= subprocess.call(['rm','-fr', kraken_result_file])
               p3_7= subprocess.call(['rm','-fr', kraken_sorted_for_krona])
    try:
        cover(run_analysis_folder+"/", run_folder_name)
    except:
        print("No coverage file to check... proceeding...")
    # delete = del_list();
    # for each in delete:
    #     subprocess.call("rm " + each, shell = True)
    print("complete")


def Upload_to_Irida(directory,irida):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    print(directory)
    print("dd"+run_folder_name)
    try:
        resp_check1 =subprocess.call(['python',irida,'-i',directory],shell=False)
        if resp_check1 == 0:
            print("data has been submitted to IRIDA")
    except:
        print("Error! please check connection")
        
        

#helper functions#############################################################


#Check genus length from list of known quantities
def get_genus_length(genus):
    lower_genus = genus.lower()
    s_config = sequdas_config()
    try:
        return s_config['genus'][lower_genus]
    except:
        return "INVALID GENUS"

#density functions

#creates dictionary for reads(key) and lanes(values)
#expects that density reading will follow third occurence of "," on a line 
def create_dict(summary_file):
    f = open(summary_file, 'r')
    lines = f.readlines()
    f.close()
    density_list = []
    density_dict = {}
    read_count = 0
    check = False
    for element in lines:
        #looks for density to assign read number
        if check is False:
            if element.find("Density") != -1:
                read_count += 1
                check = True
                continue
        #verify that line should be scanned for value
        if check:
            if get_value(element, ",", 3):
                #iteravely append values to list for a read
                density_list.append(get_value(element, ",", 3))
            else:
                #no more values in read or invalid entry, update dictionary, reset list for next read
                check = False
                density_dict.update({"read" + str(read_count):density_list})
                density_list = []
    return density_dict

#find string after nth occuence of substring
def find_occurence(string, substring, n):
    if( n == 1 ):
        return string.find(substring)
    else:
        return string.find(substring,find_occurence(string, substring, n - 1) + 1)

#gets integer after the nth occurence of a substring in a string
def get_value(string, substring, n):
        index = (find_occurence(string, substring, n)) + 1
        secondary_index = index
        while (string[secondary_index]).isdigit():
            secondary_index += 1
        if (string[index:secondary_index]).isdigit():
            return string[index:secondary_index]
            
#get mean of all values in dict
def get_mean(dict):
    temp_list = list(dict.values())
    temp_list = sum(temp_list, [])
    average=Average(temp_list)
    return int(average)

#read file and create list for lines removing whitespaces
def read_file_inline(string):
    lines = []
    with open(string, 'rt') as in_file:
        for line in in_file:
            lines.append(line.replace(' ', ''))
    return lines
def Average(lst):
    for i in range(0, len(lst)): 
        lst[i] = int(lst[i]) 
    return sum(lst) / len(lst)         
#coverage functions
#Create list of dictionaries for information on each sample, contains...
#Read_length, coverage_estimation, sample_number, sample_id, genus_length, genus, number_of_reads
def create_sample_dict(directory):
    list_dict_sample = []
    rough_list = read_data_csv(directory)
    genus_list = make_genus_list(rough_list)
    sample_list = make_sample_list(rough_list)
    fastq_dictionary = make_fastq_dict(directory)
    for index, each_sample in enumerate(sample_list):
        if len(sample_list) == 0:
            return "N/A"
        if isinstance(each_sample, basestring):
            dict = {}
            dict["sample_id"] = each_sample
            dict["sample_number"] = index + 1
            print("Processing sample: " + str(index + 1))
            read_length_store = read_length(each_sample, fastq_dictionary, directory)
            #reads_store = reads(each_sample, index + 1 )
            dict["read_length"] = read_length_store
            #dict["number_of_reads"] = reads_store
            dict["genus"] = genus_list[index]
            genus_length = get_genus_length(genus_list[index ])
            dict["genus_length"] = genus_length
            if genus_length != "INVALID GENUS":
                length = (int(read_length_store)/int(genus_length))
                dict["coverage_estimation"] = str(length)
            else:
                dict["coverage_estimation"] = "Genus length is not in Sequdas but can be added in Config"
            print(dict)
            list_dict_sample.append(dict)
    return list_dict_sample

#versioned for cluster
def create_sample_dict_cluster(directory, run_analysis_folder, run_folder_name):
    list_dict_sample = []
    rough_list = read_data_csv(directory)
    genus_list = make_genus_list(rough_list)
    sample_list = make_sample_list(rough_list)
    fastq_dictionary = make_fastq_dict(directory)
    for index, each_sample in enumerate(sample_list):
        if len(sample_list) == 0:
            return "N/A"
        if isinstance(each_sample, basestring):
            dict = {}
            dict["sample_id"] = each_sample
            dict["sample_number"] = index + 1
            start = "$$$"
            end = "delete.txt"
            read_length_store = 0
            for f in os.listdir(run_analysis_folder):
                if (f[f.find(start)+len(start):f.rfind(end)]) == each_sample:
                    name = run_analysis_folder+"/"+run_folder_name+"_$$$"+each_sample+"delete.txt"
                    file = read_file_inline(name)
                    for line in file:
                        read_length_store = line
                    os.remove(name)
            dict["read_length"] = read_length_store
            dict["genus"] = genus_list[index]
            genus_length = get_genus_length(genus_list[index])
            dict["genus_length"] = genus_length
            if genus_length != "INVALID GENUS":
                length = (int(read_length_store)/int(genus_length))
                dict["coverage_estimation"] = str(length)
            else:
                dict["coverage_estimation"] = "Genus length is not in Sequdas but can be added in Config"
            print(dict)
            list_dict_sample.append(dict)
    return list_dict_sample

#create dictionary for fastqfiles in folder directory with sample id as key for file name
def make_fastq_dict(directory):
    run_folder_name=os.path.basename(os.path.normpath(directory))
    fastq_file_location=directory+"/Data/Intensities/BaseCalls/"
    fastq_files = os.listdir(fastq_file_location)
    fastq_file_dict = {}
    for fastq_file in fastq_files:
        if fastq_file.endswith(".fastq.gz"):
            matchObj = re.match( r'(.*)\_S\d+\_L\d{3}\_(R\d+)\_\S+(fastq.gz)', fastq_file, re.M|re.I)
            if matchObj:
                if(matchObj.group(2)=="R1" or matchObj.group(2)=="R2"):
                    key=matchObj.group(1)+"_"+matchObj.group(2)
                    fastq_file_dict[key]=fastq_file
    return fastq_file_dict

#Get read length of sample
def read_length(sample_id, dict, dir):
    fastq_file_location= dir+"/Data/Intensities/BaseCalls/"
    path_f = dict[sample_id + "_R1"]
    path_f = fastq_file_location + path_f
    read_length_F = int(subprocess.check_output("zcat "+path_f+" | paste - - - - | cut -f 2 | tr -d '\n' | wc -c", shell = True))
    path_r = dict[sample_id + "_R2"]
    path_r = fastq_file_location + path_r
    read_length_R = int(subprocess.check_output("zcat "+path_r+" | paste - - - - | cut -f 2 | tr -d '\n' | wc -c", shell = True))
    read_length = read_length_F + read_length_R
    return read_length

#Get number of reads for sample
"""
def reads(sample_id, sample_number):
    path = "Data/Intensities/Basecalls/"+sample_id+"_S"+str(sample_number)+"_L001_R1_001.fastq.gz"
    reads = int(subprocess.check_output("zcat "+path+" |wc -l", shell = True))/4
    return reads
"""
#read csv file from string and make rough list from data
def read_data_csv(directory):
    with open(directory  + '/SampleSheet.csv', 'rb') as file:
        reader = csv.reader(file)
        arr = list(reader)
        rough_list = []
        check = True
        try:
            for element in arr:
                try:
                    if element[0] == '':
                        check = True
                    if element[0] == "Sample_ID":
                        check = False
                    if check == False:
                        rough_list.append(element)
                except:
                    continue
        except:
            print("There was an error parsing the Sample Sheet")
    return rough_list

#parse rough list to get sample id list
def make_sample_list(list):
    sample_list = []
    for element in list:
        if element[0] != "Sample_ID":
            addition = re.sub(r"_", '-', element[0])
            addition = re.sub(r"/", '-', addition)
            addition = re.sub(r"\.", '-', addition)
            addition = re.sub(r" ", '-', addition)
            addition = re.sub(r"\s+", '-', addition)
            sample_list.append(addition)
    if sample_list[0] == "":
        sample_list = []
        for element in list:
            if element[0] != "Sample_ID":
                sample_list.append(element[1])
    return sample_list

#parse rough list to get genus list
def make_genus_list(list):
    genus_list = []
    index = None
    start = "GENUS='"
    end = "'; "
    for x, each in enumerate(list[0]):
        if each == "Description":
            index = x
    for element in list:
        if index is not None:
            if element[index] != "Description":
                s = element[index]
                genus_list.append(s[s.find(start)+len(start):s.rfind(end)])
        else:
            genus_list.append(None)
    return genus_list

#adjust coverage for kraken
def cover(name,coverage):
    with open(name+coverage+"_coverage.txt") as data:
        cover = json.load(data)
    new = []
    for each in cover:
        dict = {}
        for key, value in each.iteritems():
            if key =="coverage_estimation":
                if value =="Genus length is not in Sequdas but can be added in Config":
                    genus = genus_kraken(name+each["sample_id"] +"_kraken2_report.txt")
                    if get_genus_length(genus) != "INVALID GENUS":
                        coverage_est = int(each["read_length"])/int(get_genus_length(genus))
                        value = "Genus in sample sheet was not found, however Kraken2 estimted coverage as: "+ str(coverage_est)
            dict[key] = value
        new.append(dict)
    with open(name+coverage+"_coverage.txt", 'w') as outfile: 
        json.dump(new, outfile)

#parse kraken report for genus
def genus_kraken(name):
    f = open(name,"r")
    for x,each in enumerate(f):
        if re.search("\sG\s", each):
            str = each
            break
    str = re.split("\s",str)
    str_empt = [x.strip() for x in str]
    str = [x for x in str_empt if x]
    str = str[5]
    return str

#code to filter sample sheet
def filter_sheet(input_dir, output_dir):
    folder = os.path.basename(os.path.normpath(input_dir))
    inp = input_dir+"/SampleSheet.csv"
    out = output_dir +"/"+folder
    try:
        with open(inp, "rb") as input, open(out + "/newfile.csv", "wb") as output:
            reader = csv.reader(input)
            writer = csv.writer(output)
            for index, row in enumerate(reader):
                #we are only interested in area after 20
                if index > 21:
                    #code to filter area of interest
                    try:
                        if row[0] != '':
                            if len(row) > 7:
                                temp = row[8:]
                                row[7] = row[7] + (';'.join(temp))
                                del row[8:]
                                writer.writerow(row)
                    except:
                        continue
                else:
                    writer.writerow(row)
            #keep old file, output new
            os.rename(out + '/SampleSheet.csv',out + '/SampleSheet_pre.csv')
            os.rename(out + '/newfile.csv',out + '/SampleSheet.csv')
    except:
        ""
        
#check that cluster job has finished
def wait_until(job):
    regex = u'<JB_name>(.+?)</JB_name>+?'
    qlist = subprocess.check_output("qstat -xml", shell =True)
    names = re.findall(regex, qlist)
    while job in names:
        time.sleep(5)
        regex = u"<JB_name>(.+?)</JB_name>+?"
        qlist = subprocess.check_output("qstat -xml", shell =True)
        names = re.findall(regex, qlist)

#delete files created by cluster after running
def del_list():
    keep = ["test_result", "result", "Lib", "Conf", "Log","result", "sequdas_server.py", "Cluster", "kraken_parse.py", "kaiju_parse.py","compare.py"]
    files = [f for f in os.listdir('/data/sequdas/sequdas_server') if (os.path.isfile(f) and f not in keep)]
    return files

#check if qsub had an error
def check_up(qdir):
    error_list = []
    del_list = []
    for f in os.listdir(qdir):
        with open(qdir + "/"+f, "r") as file:
            temp = str(file.read()).lower()
            if temp.find("not found") == -1 and temp.find("error") == -1:
                del_list.append(f)
            else:
                error_list.append(f)
    for each in del_list:
        subprocess.call("rm " +qdir + "/"+ each, shell = True)
    if len(error_list) == 0:
        return False
    else:
        return True