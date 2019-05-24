import org.apache.commons.cli.*;

public class RunLoadData {
    public static void main(String[] args) {
        int NUMBER_OF_THREADS = 1;


        Options options = new Options();

        Option threadOpt = new Option("t", "thread", true, "number of threads. default is 1");
        threadOpt.setRequired(true);
        options.addOption(threadOpt);

        Option typeRequestOpt = new Option("r", "type_request", true, "type of request (sum, avg, etc.)");
        typeRequestOpt.setRequired(true);
        options.addOption(typeRequestOpt);


        Option latencyTypeOpt = new Option("l", "latency_type", true, "latency type");
        latencyTypeOpt.setRequired(false);
        options.addOption(latencyTypeOpt);


        Option packetlossTypeOpt = new Option("p", "packetloss_type", true, "packet loss type");
        packetlossTypeOpt.setRequired(false);
        options.addOption(packetlossTypeOpt);

        CommandLineParser parser = new DefaultParser();
        HelpFormatter formatter = new HelpFormatter();
        CommandLine cmd;

        try {
            cmd = parser.parse(options, args);

            Integer thread = Integer.parseInt(cmd.getOptionValue("thread"));
            String typeRequest = cmd.getOptionValue("type_request");
            String latencyType = cmd.getOptionValue("latency_type");
            String packetlossType = cmd.getOptionValue("packetloss_type");

            for (int i = 1; i < 1 + thread; i++) {
                BulkLoadAndRetrieveDataRunnable lr = new BulkLoadAndRetrieveDataRunnable(i, thread, typeRequest, latencyType, packetlossType);
                lr.start();
            }
        } catch (ParseException e) {
            System.out.println(e.getMessage());
            formatter.printHelp("utility-name", options);
            System.exit(1);
        }


//        for (int i = 1; i < NUMBER_OF_THREADS+1; i++) {
//            LoadDataRunnable lr = new LoadDataRunnable(i, NUMBER_OF_THREADS);
//            lr.start();
//        }
//
//        for (int i = 1; i < NUMBER_OF_THREADS+1; i++) {
//            RetrieveDataRunnable lr = new RetrieveDataRunnable();
//            lr.start();
//        }


    }
}
