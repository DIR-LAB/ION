



###################################################################################################
#Issue Diagnosis prompt templates.
###################################################################################################
ISSUE_TEMPLATES = {
    'Small I/O': "HPC I/O works in the following way: All the ranks (processes) running on different computing nodes will issue multiple I/O requests to different OST servers, which are the storage servers. \
                The I/O requests will be transferred using RPC (remote procedure call).  If an I/O request is smaller than the RPC size, it will be aggregated with others before being sent to the OSTs if they are \
                sequential meaning the issue of small requests is largely mitigated automatically. Otherwise, it may lead to inefficient use of the RPC channel since a RPC transfer includes connection building and \
                destroying overheads. The small I/O can mostly be ignored if the application only accesses a file once or twice via small I/O requests, because it is common for an application to load small configuration \
                file, which tends to create small I/O requests. However, repetitive I/O requests to the same file which are significantly smaller than the RPC size may be an issue. Note that, the system on which the \
                trace was collected is configured with a page size of 4kb and max_pages_per_rpc set to 1024, which indicates that the maximum RPC size is 4MB.\n\
                To diagnose the issue, first analyze the size of the I/O requests, then check to see if any of the requests identified as small are accessing the same files multiple times, and finally check if any of the \
                small requests might be aggregated based on their access patterns.",

    'Random I/O': "HPC I/O works in the following way: All the ranks (processes) running on different computing nodes will issue multiple I/O requests to different OST servers, which are the storage servers. \
                The I/O requests will be transferred using RPC (remote procedure call). When applications send I/O requests they are usually buffered in local memory and may be aggregated with other I/O requests \
                if they target nearby pages. If the I/O requests, aggregated or not, are equal to or larger than the maximum RPC size, they fully utilize the RPC channel and the server-side buffer. \
                However, I/O requests which are significantly smaller than the RPC size after aggregation do not use the RPC channel effectively and may lead to I/O performance issues. Additionally, \
                this issue is only of concern when the described behavior is highly repetitive as it does not impact performance if such I/O patterns are only used to access a file a small number of times. \
                Specifically, this type of issue is often referred to as a random access pattern issue.. Note that, the system on which the trace was collected is configured with a page size of 4kb and max_pages_per_rpc set to 1024, which indicates that the maximum RPC size is 4MB.\n\
                Please use the provided information and think step by step to diagnose whether the attached trace file contains any random access patterns which may be cause for concern.",

    'Load Imbalanced I/O': "HPC I/O works in the following way: All the ranks (processes) running on different computing nodes will issue multiple I/O requests to different OST servers, which are the storage servers. \
                The I/O requests will be transferred using RPC (remote procedure call). If multiple ranks are requesting I/O operations concurrently but their sizes are unbalanced, it may lead some ranks to \
                issue more I/O requests in a given time interval which may become a bottleneck. This is known as a load balance issue. However, in some cases, a set of ranks may process much faster than others \
                so it is beneficial for  these ranks to account for a larger share of I/O requests so it is very important to roughly measure the speed of the various ranks by analyzing throughput or I/O operations \
                per second for each one prior to making any judgements regarding any load balance issues.\n\
                Please use the provided information and think step by step to diagnose whether the attached trace file contains any load imbalanced I/O behavior which may be cause for concern.",

    'Shared File I/O': "HPC I/O works in the following way. All the ranks (processes) running on different computing nodes will issue multiple I/O requests to different OST servers, which are the storage servers. \
                The OST servers split data files into chunks which are known as stripes, where each stripe has a size of stripe_size the stripes of a file are stored across stripe_count different OST servers. \
                If the I/O requests target different files, then they are called independent file accesses. If they target different regions of the same file, then they are called shared file accesses. \
                Generally, independent file accesses are more efficient because each process conducts I/O independently towards its own file. But, if there are too many processes reading and writing to too many \
                independent files, the metadata load may become an issue as the load on the metadata servers may be very high. Since shared file accesses only access one file, the metadata servers will not \
                have a very high load, but many processes accessing the same file may complicate data access for the OSTs. This is because these processes may access overlapping areas of the file, introducing \
                conflicts and lock overheads. Even if these requests are not overlapped, they may be accessing the same data stripe of the file (i.e. two request offsets are within the range of the stripe size of \
                the file). This will also lead to lower performance as they introduce conflicts. The I/Os will be sent to the same OST server as well, reducing the parallelism. The files accessed in the application trace have a stripe_size of 1MB and a stripe_count of 1.\n\
                To identify if an application has shared file issue, we need to take following items into consideration\n\
                    1. Many or all processes access the same file. \n\
                    2. Accessing the same file happens repeatedly.\n\
                    3. Requests from different processes are overlapped in terms of time.\n\
                    4. Requests from different processes fall into the same file stripe, i.e., the offsets of these requests are within the stripe size of the file. The stripe size is 1MB.\n\
                Please use the provided information and think step by step to diagnose whether the attached trace file contains any shared file I/O behavior which may be cause for concern.",

    'High Metadata I/O': "HPC I/O works in the following way. All the ranks (processes) running on different computing nodes will issue metadata I/O requests to different MDS servers, which are the metadata servers. \
                If an application has a high metadata issue, it means that the application is issuing a large number of metadata I/O requests or spending a lot of time conducting metadata operations. \
                If the amount metadata operations approaches the total size or amount of regular I/O operations and these are in quick succession, it may cause uneccessary strain on the metadata servers, \
                and in extreme cases, it may create a bottleneck for the application an the system.\n\
                To identify if an application has a high metadata issue, we need to take following items into consideration\n\
                    1. The amount of time conducting metadata operations is similar to that of regular I/O operations\n\
                    2. The number of metadata operations is comparable to regular I/O operations and both are significant.\n\
                    3. The amount of time conducting metadata operations is significant to the total runtime of the application.\n\
                Please use the provided information and think step by step to diagnose whether the attached trace file contains any high metadata I/O behavior which may be cause for concern.",

    "Misaligned I/O": "As HPC applications rely on a shared parallel file system (e.g., Lustre, GPFS) to store and retrieve data, and those use a technique called data stripping to increase \
                performance, block/striped aligned I/O requests are important to avoid lock contention (false data sharing). As stripes can be located in different servers, unaligned requests \
                can require multiple servers to complete an operation and introduce inefficiencies. Darshan exposes two POSIX counters to capture mis-aligned memory (POSIX_MEM_NOT_ALIGNED) and \
                file (POSIX_FILE_NOT_ALIGNED) accesses. Please use the provided information and think step by step to diagnose whether the attached trace file contains any misaligned I/O behavior which may be cause for concern.",

    "Non-Collective I/O": "HPC I/O works in the following way. All the ranks (processes) running on different computing nodes will issue multiple I/O requests to different OST servers, which \
                are the storage servers. The I/O requests will be transferred using RPC (remote procedure call). Since it is often the case that multiple ranks need to conduct I/O in parallel, \
                it is often beneficial to use MPI-IO to abstract away the intricate details of conducting efficient parallel I/O. However, it is important to consider if it is potentially \
                useful to use such abstractions at all based on the configured environment, and, if it is useful, whether or not they are used properly to maximize their benefits. \
                To classify if the configuration could benefit from the use of MPI-IO it is useful to analyze the number of ranks used by the application since the use of only one rank is \
                unlikely to benefit from parallel I/O libraries. In case multiple ranks are used, it is important to consider if MPI-IO is being used effectively by analyzing the amount of \
                collective I/O operations and non-blocking operations as these have the highest potential to leverage MPI-IO effectively.\n\
                Please use the provided information and think step by step to diagnose whether the attached trace information points towards the ineffective use of MPI-IO.",

    "Low Level Library Usage": "HPC I/O works in the following way. All the ranks (processes) running on different computing nodes will issue multiple I/O requests to different OST servers, \
                which are the storage servers. The I/O requests will be transferred using RPC (remote procedure call). Due to the many details related to conducting efficient I/O higher \
                level I/O libraries, which are built to abstract some of these difficulties, are generally preferred. In general, excessive use of the lowest level library, STDIO, should \
                be avoided. In case STDIO is being used, it's use should be compared to that of other, higher level libraries to provide context regarding how much it is used throughout the entire application.\n\
                Please use the provided information and think step by step to diagnose whether the attached trace information files point towards the excessive use of low level I/O libraries."                      
}



###################################################################################################
#Issue Diagnosis Summarization Prompt template.
###################################################################################################
SUMMARY_TEMPLATE = "You are an expert in HPC I/O performance analysis. You will be given a list of diagnosis summaries for a number of different I/O related issues originating from the same application trace log. \
                    Your job is to carefully analyze each of these summaries and form a conclusion which indicates the most prominent I/O performance issues for the underlying application. \n\
                    Be sure to consider the following in your summary: \n\
                        1. If specific issues or all issues seem to to insignificant, be sure to indicate that in your summary. \n\
                        2. keep your summary brief and to the point. \n\
                    Here is the list of summaries, organized by issue type: \n"



###################################################################################################
#File format and response formatting hints templates.
###################################################################################################
COLUMN_ADVICE = "Any counter that has a value of -1 indicates that Darshan could not monitor that counter, and its value should be ignored. Only for the rank column, a value of -1 indicates that the file is shared across all processes and statistics are aggregated. \n"

FILE_DESCRIPTION = "I have attached a csv file which you can load into a dataframe using pandas. The csv contains I/O trace information from an application run on an HPC system and the data was collected using darshan. The data contains the following columns:"

RESPONSE_ADVICE = "Before claiming that an issue is significant, it is important to consider the following: \n\
                    1. Does the issue affect a significant portion of the entire application's I/O operations? If the issue is only present in a small portion of the I/O operations, it may not be a significant issue. \n\
                    2. Is the issue a result of the application's I/O behavior or is it likely a result of the system's configuration? If the issue is a result of the system's configuration, it may not be possible to feasible the issue without reconfiguring the system.\n"
                    
RESPONSE_FORMAT= "Following your analysis, write a brief summary of your diagnosis strictly in the following format:\n\
                        Diagnosis: <summary of your diagnosis>"



###################################################################################################
#Continued analysis prompt templates. 
#The LLM is given a question based on the diagnosis they provided in the initial task.
###################################################################################################
CONTINUED_ANALYSIS_START = "You are an expert in HPC I/O performance analysis. You are helping me diagnose I/O performance issues in an application trace log. You have already analyzed the trace log and provided a diagnosis for all of the issues. \
                            I will ask you a question about the analysis you provided. Here are some of the details of the analysis you provided for each of the I/O issues you analyzed: \n"
CONTINUED_ANALYSIS_END = "Here is the question you must answer: \n"



###################################################################################################
#Module mapping for each issue.
#Each issue is associated with a list of modules that are relevant to the diagnosis of that issue.
###################################################################################################
MODULE_MAP = {
    "Small I/O": ['DXT'],
    "Random I/O": ['DXT'],
    "Load Imbalanced I/O": ['DXT'],
    "Shared File I/O": ['DXT'],
    "High Metadata I/O": ['DXT', 'POSIX'], 
    "Misaligned I/O": ['POSIX'],
    "Non-Collective I/O": ['DXT', 'MPI-IO'],
    "Low Level Library Usage": ['POSIX', 'MPI-IO', 'STDIO', 'H5F']
}
