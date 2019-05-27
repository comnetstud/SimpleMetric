import kx.c;

import java.io.*;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class BulkLoadAndRetrieveDataRunnable implements Runnable {
    private Thread t;
    private Integer number;
    private Integer totalNumber;
    private String typeRequest;
    private String latencyType;
    private String packetlossType;

    BulkLoadAndRetrieveDataRunnable(Integer number, Integer totalNumber, String typeRequest, String latencyType, String packetlossType) {
        this.number = number;
        this.totalNumber = totalNumber;
        this.typeRequest = typeRequest;
        this.latencyType = latencyType;
        this.packetlossType = packetlossType;
    }

    public void run() {
        long timestampFrom = 1546300800 + (number - 1) * 86400;
        long timestampTo = 1546300800 + number * 86400;
        java.util.Date dateFrom = new java.util.Date(timestampFrom * 1000);
        java.util.Date dateTo = new java.util.Date(timestampTo * 1000);
        SimpleDateFormat dt = new SimpleDateFormat("yyyy.MM.dd'D'hh:mm:ss");
        try {
            c c = new c("localhost", 5000);
//            c.k()
            StringBuilder sb = new StringBuilder("ssdata:([] timestamp:()");
            for (int i = 1; i < 11; i++) {
                sb.append(String.format(";sensor%03d:()", i));
            }
            sb.append(")");

            c.k(sb.toString());
            c.k(".u.upd:insert");
            BufferedReader reader;
            try {
                StringBuilder network = new StringBuilder();
                if (latencyType != null) {
                    network.append("_").append(latencyType).append("_").append(packetlossType);
                }
                File analysisFile = new File("../analysis/kdb/latency_meter/latency_meter_" + number + "_" + totalNumber + "_" + typeRequest + network.toString() + ".txt");
                analysisFile.createNewFile();

                FileWriter fileWriter = new FileWriter(analysisFile);
                PrintWriter printWriter = new PrintWriter(fileWriter);


                reader = new BufferedReader(new FileReader("../data/csv/csv_1sec_" + number + "d.dat"));
                String line = reader.readLine();
                int count = 0;
                while (line != null) {
                    if (count > 100)
                        break;
//                    System.out.println(line);
                    // read next line
                    List<List> dataList = new ArrayList<List>();
                    for (int i = 0; i < 11; i++) {
                        dataList.add(new ArrayList());
                    }
                    for (int i = 0; i < 100; i++) {
                        line = reader.readLine();
                        if (line != null) {
                            String[] lline = line.split(";");
                            int listCount = 0;
                            for (String d : lline) {
                                if (listCount == 0) {
                                    java.util.Date date = new java.util.Date(Long.parseLong(lline[0]) * 1000);
                                    dataList.get(listCount).add(dt.format(date));
                                } else {
                                    dataList.get(listCount).add(new Float(d));
                                }
                                listCount++;
                            }
                        }
                    }
                    Object[] listObj = new Object[11];
                    int listCount = 0;
                    for (List list : dataList) {
                        listObj[listCount] = list.toArray();
                        listCount++;
                    }
                    long startTime = System.nanoTime();
                    /* ... the code being measured starts ... */
//                    System.out.println(sb.toString());
//                    c.ks("cpu", listObj);
                    c.ks(".u.upd", "ssdata", listObj);

                    long bulkTime = System.nanoTime();
                    if (typeRequest.equals("sum")) {
                        c.ks("select sum sensor001 from ssdata where timestamp>=`" + dt.format(dateFrom) + ",timestamp<`" + dt.format(dateTo));
                    } else if (typeRequest.equals("count")) {
                        c.ks("count select from  ssdata where timestamp>=`" + dt.format(dateFrom) + ",timestamp<`" + dt.format(dateTo));
                    } else if (typeRequest.equals("avg")) {
                        c.ks("select avg sensor001 from ssdata where timestamp>=`" + dt.format(dateFrom) + ",timestamp<`" + dt.format(dateTo));
                    } else if (typeRequest.equals("max")) {
                        c.ks("select max sensor001 from ssdata where timestamp>=`" + dt.format(dateFrom) + ",timestamp<`" + dt.format(dateTo));
                    }

                    long endTime = System.nanoTime();

                    printWriter.print(String.format("%d\t%d\t%d\t%d\n", count, endTime - startTime, bulkTime - startTime, bulkTime - endTime));
//                    System.out.println(count*100);
                    count++;
                }
                reader.close();
                printWriter.close();
            } catch (IOException e) {
                e.printStackTrace();
            }

            c.close();
        } catch (Exception e) {
            e.printStackTrace();
        }


    }

    public void start() {
        System.out.println("Starting " + number);
        if (t == null) {
            t = new Thread(this);
            t.start();
        }
    }
}
