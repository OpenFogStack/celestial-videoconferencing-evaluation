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
	"encoding/json"
	"fmt"
	"math"
	"net/http"

	log "github.com/sirupsen/logrus"
)

func getActiveSats(shells int, gateway *string) ([]map[int]struct{}, error) {

	active := make([]map[int]struct{}, shells)

	for s := 0; s < shells; s++ {
		active[s] = make(map[int]struct{})

		resp, err := http.Get(fmt.Sprintf("http://%s/shell/%d", *gateway, s))

		if err != nil {
			log.Error(err.Error())
			return active, err
		}

		if resp.StatusCode != 200 {
			err = fmt.Errorf("got status %d when looking for shell info on %d", resp.StatusCode, s)
			log.Error(err.Error())
			resp.Body.Close()
			return active, err
		}

		var info struct {
			ActiveSats []struct {
				Shell int
				Sat   int
			}
		}

		err = json.NewDecoder(resp.Body).Decode(&info)

		resp.Body.Close()

		if err != nil {
			log.Error(err.Error())
			return active, err
		}

		for _, v := range info.ActiveSats {
			active[s][v.Sat] = struct{}{}
		}
	}

	return active, nil
}

func getScore(shell int, sat int, id string, gateway *string) (float64, float64, error) {
	// log.Debugf("looking for path from gst %s to sat %d %d", id, shell, sat)

	resp, err := http.Get(fmt.Sprintf("http://%s/path/gst/%s/%d/%d", *gateway, id, shell, sat))

	if err != nil {
		log.Error(err.Error())
		return 0.0, 0.0, err
	}

	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		if resp.StatusCode != 404 {
			err = fmt.Errorf("got status %d when looking for path from gst %s to sat %d in shell %d", resp.StatusCode, id, sat, shell)
			log.Error(err.Error())
		}

		return 0.0, 0.0, err
	}

	var info struct {
		Paths []struct {
			Delay float64
		}
	}

	err = json.NewDecoder(resp.Body).Decode(&info)

	if err != nil {
		log.Error(err.Error())
		return 0.0, 0.0, err
	}

	if len(info.Paths) == 0 {
		log.Error("no path found?")
		return 0.0, 0.0, err
	}

	// find minimum delay
	minDelay := math.MaxFloat64

	for _, p := range info.Paths {
		if p.Delay < minDelay {
			minDelay = p.Delay
		}
	}

	// log.Debugf("delay %f, score %f, for path from gst %s to sat %d %d", minDelay, minDelay * minDelay, id, shell, sat, )

	return minDelay * minDelay, minDelay, nil
}

func getGSTDist(name string, id string, gateway *string) (float64, error) {
	// log.Debugf("looking for path from gst %s to gst %s", id, name)

	resp, err := http.Get(fmt.Sprintf("http://%s/path/gst/%s/gst/%s", *gateway, id, name))

	if err != nil {
		log.Error(err.Error())
		return 0.0, err
	}

	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		if resp.StatusCode != 404 {
			err = fmt.Errorf("got status %d when looking for path from gst %s to gst %s", resp.StatusCode, id, name)
			log.Error(err.Error())
		}

		return 0.0, err
	}

	var info struct {
		Paths []struct {
			Delay float64
		}
	}

	err = json.NewDecoder(resp.Body).Decode(&info)

	if err != nil {
		log.Error(err.Error())
		return 0.0, err
	}

	if len(info.Paths) == 0 {
		log.Error("no path found?")
		return 0.0, err
	}

	// find minimum delay
	minDelay := math.MaxFloat64

	for _, p := range info.Paths {
		if p.Delay < minDelay {
			minDelay = p.Delay
		}
	}

	// log.Debugf("delay %f, for path from gst %s to gst %s", minDelay, minDelay * minDelay, id, name)

	return minDelay, nil
}

func getShellNum(gateway *string) int {
	resp, err := httpClient.Get(fmt.Sprintf("http://%s/info", *gateway))

	if err != nil {
		log.Error(err.Error())
		panic(err)
	}

	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		err = fmt.Errorf("got status %d when looking for info", resp.StatusCode)
		log.Error(err.Error())
		panic(err)
	}

	var constellation struct {
		Shells int
	}

	err = json.NewDecoder(resp.Body).Decode(&constellation)

	if err != nil {
		log.Error(err.Error())
		panic(err)
	}

	return constellation.Shells
}
