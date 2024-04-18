/*
* This file is part of Celestial's Videoconferencing Evaluation
* (https://github.com/OpenFogStack/celestial-videoconferencing-evaluation).
* Copyright (c) 2021 Tobias Pfandzelter, The OpenFogStack Team.
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, version 3.
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
* General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
**/

package main

import (
	"bufio"
	"flag"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"

	log "github.com/sirupsen/logrus"
)

const BUFFERSIZE = 4096

type client struct {
	addr string
	udp  int
	http int
}

var httpClient *http.Client

func writer(l <-chan string) {

	f, err := os.Create("out.csv")
	if err != nil {
		log.Fatal(err)
	}
	w := bufio.NewWriter(f)
	_, err = w.WriteString("t,shell,sat,path1,path1dist,path2,path2dist,path3,path3dist\n")

	errlog := log.New()
	errlog.Out = os.Stderr

	if err != nil {
		log.Error(err.Error())
		return
	}

	ticker := time.Tick(5 * time.Second)

	for {
		select {
		case str := <-l:
			_, err := w.WriteString(str)

			if err != nil {
				errlog.Errorf(err.Error())
			}
		case <-ticker:
			err := w.Flush()

			if err != nil {
				errlog.Errorf(err.Error())
			}
		}
	}
}

func inform(id string, httpPort int, shell int, sat int) error {

	v := make(url.Values)

	v.Set("server", fmt.Sprintf("%d.%d.celestial", sat, shell))
	v.Set("satID", fmt.Sprintf("%d", sat))
	v.Set("shellID", fmt.Sprintf("%d", shell))

	c, err := httpClient.PostForm(fmt.Sprintf("http://%s.gst.celestial:%d", id, httpPort), v)

	if err != nil {
		log.Error(err.Error())
		return err
	}

	c.Body.Close()

	return nil
}

func informNone(id string, httpPort int) error {

	v := make(url.Values)

	v.Set("server", "none")

	c, err := httpClient.PostForm(fmt.Sprintf("http://%s.gst.celestial:%d", id, httpPort), v)

	if err != nil {
		log.Error(err.Error())
		return err
	}

	c.Body.Close()

	return nil
}

var clients map[string]client

func updateClientsAlt(interval *int, gateway *string) {
	start := time.Now()

	l := make(chan string, BUFFERSIZE)

	go writer(l)

	for {
		updateTime := time.Since(start)

		log.Infof("Update took %f seconds", updateTime.Seconds())

		time.Sleep((time.Duration(*interval) * time.Second) - updateTime)

		start = time.Now()
		// no clients? keep on waiting
		if len(clients) == 0 {
			log.Debugf("no clients yet, continuing...")
			continue
		}

		log.Debug("Informing clients of satellite server.gst.celestial")
		for id, c := range clients {
			v := make(url.Values)

			v.Set("server", "server.gst.celestial")
			v.Set("satID", "4")
			v.Set("shellID", "0")

			c, err := httpClient.PostForm(fmt.Sprintf("http://%s.gst.celestial:%d", id, c.http), v)

			if err != nil {
				log.Error(err.Error())
				continue
			}

			c.Body.Close()
		}

		str := ""

		// t
		str += strconv.Itoa(int(time.Now().UnixNano()))
		str += ","

		// shell
		str += "-1"
		str += ","

		// sat
		str += "4"
		str += ","

		dist := make(map[string]float64)

		for id := range clients {
			d, err := getGSTDist("server", id, gateway)

			if err != nil {
				log.Error(err.Error())
				break
			}

			dist[id] = d

		}

		// path1
		str += ","
		// path1dist
		str += strconv.FormatFloat(dist["1"], 'f', -1, 64)
		str += ","
		// path2
		str += ","
		// path2dist
		str += strconv.FormatFloat(dist["2"], 'f', -1, 64)
		str += ","
		// path3
		str += ","
		// path3dist
		str += strconv.FormatFloat(dist["3"], 'f', -1, 64)
		str += "\n"

		l <- str
	}
}

func updateClients(interval *int, gateway *string) {

	shells := getShellNum(gateway)

	start := time.Now()

	l := make(chan string, BUFFERSIZE)

	go writer(l)

	for {
		updateTime := time.Since(start)

		log.Infof("Update took %f seconds", updateTime.Seconds())

		time.Sleep((time.Duration(*interval) * time.Second) - updateTime)

		start = time.Now()
		// no clients? keep on waiting
		if len(clients) == 0 {
			log.Debugf("no clients yet, continuing...")
			continue
		}

		// 1. get active satellites
		active, err := getActiveSats(shells, gateway)

		log.Debugf("got active satellites: %#v", active)

		if err != nil {
			log.Error(err.Error())
			continue
		}

		if len(clients) == 0 {
			log.Debugf("no clients yet, continuing...")
			continue
		}

		totalActive := 0

		for shell, activeSats := range active {
			log.Debugf("active satellites in shell %d: %#v", shell, activeSats)
			totalActive += len(activeSats)
		}

		if totalActive == 0 {
			log.Debugf("no active satellites yet, continueing...")
			continue
		}

		// 2. for each active satellite, find a score
		// find the one with the best score
		log.Debug("Finding sat with best score")
		var bestShell int
		var bestSat int
		var bestScore float64
		//var bestDist map[string]float64

		for shell, sats := range active {
			for sat := range sats {
				score := 0.0
				dist := make(map[string]float64)
				for id := range clients {
					s, d, err := getScore(shell, sat, id, gateway)

					if err != nil {
						log.Error(err.Error())
						score = 0.0
						break
					}

					if s == 0.0 {
						score = 0.0
						break
					}

					score += s
					dist[id] = d

				}

				if score == 0.0 {
					continue
				}

				if bestScore == 0.0 || score < bestScore {
					bestShell = shell
					bestSat = sat
					bestScore = score
					//bestDist = dist
				}
			}
		}

		if bestScore == 0.0 {
			log.Errorf("no path found!")
			log.Debug("Informing clients of no satellite")
			for id, c := range clients {
				err := informNone(id, c.http)

				if err != nil {
					log.Error(err.Error())
					continue
				}

			}

			l <- fmt.Sprintf("%d,-1,-1,,0.0,,0.0,,0.0", time.Now().UnixNano())

			continue
		}

		log.Infof("total score: %f, best sat is %d %d", bestScore, bestShell, bestSat)

		// 3. inform satellite that it has been chosen
		// log.Debugf("Informing satellite %d %d", bestShell, bestSat)
		// err = informSat(bestShell, bestSat)
		//
		//		if err != nil {
		//			log.Error(err.Error())
		//			continue
		//		}

		// 4. inform clients of new satellite
		log.Debugf("Informing clients of satellite %d %d", bestShell, bestSat)
		for id, c := range clients {
			err := inform(id, c.http, bestShell, bestSat)

			if err != nil {
				log.Error(err.Error())
				continue
			}

		}

		str := ""

		// t
		str += strconv.Itoa(int(time.Now().UnixNano()))
		str += ","

		// shell
		str += strconv.Itoa(bestShell)
		str += ","

		// sat
		str += strconv.Itoa(bestSat)
		str += ","

		_, d1, err := getScore(bestShell, bestSat, "1", gateway)

		if err != nil {
			log.Error(err.Error())
			continue
		}

		// path1
		str += ","
		// path1dist
		str += strconv.FormatFloat(d1, 'f', -1, 64)
		str += ","

		_, d2, err := getScore(bestShell, bestSat, "2", gateway)

		if err != nil {
			log.Error(err.Error())
			continue
		}

		// path2
		str += ","
		// path2dist
		str += strconv.FormatFloat(d2, 'f', -1, 64)
		str += ","

		_, d3, err := getScore(bestShell, bestSat, "3", gateway)

		if err != nil {
			log.Error(err.Error())
			continue
		}

		// path3
		str += ","
		// path3dist
		str += strconv.FormatFloat(d3, 'f', -1, 64)
		str += "\n"

		l <- str
	}
}

func main() {

	// update interval in seconds
	updateInterval := flag.Int("update-interval", 5, "how often (in seconds) to update path calculations")

	// gateway address to use the api
	gateway := flag.String("gateway", "localhost", "gateway address to use the api")

	alt := flag.Bool("alt", false, "use alternative tracker")

	flag.Parse()

	log.SetLevel(log.DebugLevel)

	httpClient = &http.Client{
		Timeout: 5 * time.Second,
	}

	clients = map[string]client{
		"1": {
			addr: "10.0.0.6",
			udp:  3000,
			http: 8000,
		},
		"2": {
			addr: "10.0.0.10",
			udp:  3000,
			http: 8000,
		},
		"3": {
			addr: "10.0.0.14",
			udp:  3000,
			http: 8000,
		},
	}

	if !*alt {
		updateClients(updateInterval, gateway)
	} else {
		updateClientsAlt(updateInterval, gateway)
	}

}
