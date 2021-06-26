names = ["Accra", "Abuja", "Yaoundé"]

types = ["","-rolling", "-log10"]

print("\n------------------------\n")
print("\nBASELINE:\n")
for t in types:
    print("\n------------------------\n")
    print(t)
    print("\n------------------------\n")
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            print("""<tr>
            <td>%s - %s</td>
            <td>
              <a href="./img/baseline/baseline%s-%d-%d.png">
                <img src="./img/baseline/baseline%s-%d-%d.png" />
              </a>
            </td>
          </tr>""" % (names[i], names[j], t, i+1, j+1, t, i+1, j+1))

    print("\n\n\n\n")
    print("\n------------------------\n")

print("\n------------------------\n")
print("\nREPRODUCIBILITY:\n")

experiment_types = ["satellite", "server"]
experiment_names = ["Satellite Server", "Cloud Datacenter"]
ids = ["sat", "cloud"]

print("\n------------------------\n")
ids = ["sat", "cloud"]
for experiment in range(2):

    print("""<h3 id="%s">%s<a href="#">↩</a></h3>""" %(ids[experiment], experiment_names[experiment]))

    for t in types:
        if t == "-rolling":
            continue
        elif t == "":
            print("""<h4 id=\"%s_latency_r\">Latency in ms (1s Rolling Median)<a href="#%s">↩</a></h4><div style="overflow-x: auto">
            <table>
                <thead>
                <th>Path</th>
                <th>Latency in ms (1s Rolling Median)</th>
                </thead>
                <tbody>""" % (ids[experiment], ids[experiment]))
            
        elif t == "-log10":
            print("""<h4 id="%s_latency_r">Latency in ms (log10 of 1s Rolling Median)<a href="#%s">↩</a></h4>
            <div style="overflow-x: auto">
            <table>
                <thead>
                <th>Path</th>
                <th>Latency in ms (log10 of 1s Rolling Median)</th>
                </thead>
                <tbody>""" % (ids[experiment], ids[experiment]))


        for i in range(3):
            for j in range(3):
                if i == j:
                    continue
                print("""
        <tr>
        <td>%s - %s</td>
        <td>
            <a href="./img/reproducibility/reproducibility%s-%s-%d-%d.png">
            <img src="./img/reproducibility/reproducibility%s-%s-%d-%d.png" />
            </a>
        </td>"""
    % (names[i], names[j], t, experiment_types[experiment], i+1, j+1, t, experiment_types[experiment] , i+1, j+1 ))

        print(""" </tbody>
            </table>
            </div>""")

print("\n\n\n\n")
print("\n------------------------\n")

print("\n------------------------\n")
print("\nCDFs:\n")

print("\n------------------------\n")
for experiment in range(2):
    print("\n------------------------\n")
    print(experiment_names[experiment])
    print("\n------------------------\n")
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            print("""<tr>
            <td>%s - %s</td>
            <td>
            <a href="./img/cdfs/cdf-%s-%d-%d-1.png">
                <img src="./img/cdfs/cdf-%s-%d-%d-1.png" />
            </a>
            </td>
            <td>
            <a href="./img/cdfs/cdf-%s-%d-%d-2.png">
                <img src="./img/cdfs/cdf-%s-%d-%d-2.png" />
            </a>
            </td>
            <td>
            <a href="./img/cdfs/cdf-%s-%d-%d-3.png">
                <img src="./img/cdfs/cdf-%s-%d-%d-3.png" />
            </a>
            </td>
        </tr>""" % (names[i], names[j], experiment_types[experiment], i+1, j+1, experiment_types[experiment], i+1, j+1,  experiment_types[experiment], i+1, j+1, experiment_types[experiment], i+1, j+1,  experiment_types[experiment], i+1, j+1, experiment_types[experiment], i+1, j+1))

print("\n\n\n\n")
print("\n------------------------\n")

print("\n------------------------\n")
print("\nAccuracy:\n")

print("\n------------------------\n")

for experiment in range(2):

    print("""<h3 id="%s">%s<a href="#">↩</a></h3>""" %(ids[experiment], experiment_names[experiment]))

    for run in ["1", "2", "3"]:

        print("""<h4 id="%s_%s">Run %s<a href="#%s">↩</a></h4>""" %(ids[experiment], run, run, ids[experiment]))

        for t in types:
            if t == "-rolling":
                continue
            elif t == "":
                print("""<h5 id=\"%s_%s_latency_r\">Latency in ms (1s Rolling Median)<a href="#%s_%s">↩</a></h5><div style="overflow-x: auto">
                <table>
                    <thead>
                    <th>Path</th>
                    <th>Latency in ms (1s Rolling Median)</th>
                    </thead>
                    <tbody>""" % (ids[experiment], run, ids[experiment], run))
                
            elif t == "-log10":
                print("""<h5 id="%s_%s_latency_rlog10">Latency in ms (log10 of 1s Rolling Median)<a href="#%s_%s">↩</a></h5>
                <div style="overflow-x: auto">
                <table>
                    <thead>
                    <th>Path</th>
                    <th>Latency in ms (log10 of 1s Rolling Median)</th>
                    </thead>
                    <tbody>""" % (ids[experiment], run, ids[experiment], run))


            for i in range(3):
                for j in range(3):
                    if i == j:
                        continue
                    print("""
          <tr>
            <td>%s - %s</td>
            <td>
              <a href="./img/accuracy/accuracy%s-%s-%s-%d-%d.png">
                <img src="./img/accuracy/accuracy%s-%s-%s-%d-%d.png" />
              </a>
            </td>"""
        % (names[i], names[j], t, experiment_types[experiment], run, i+1, j+1, t, experiment_types[experiment],run , i+1, j+1 ))

            print(""" </tbody>
                </table>
                </div>""")

print("\n\n\n\n")
print("\n------------------------\n")
    

    