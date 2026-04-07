package cgolrunner

import (
	"fmt"
	"testing"
	"time"
)

func TestGlider(t *testing.T) {

	// TODO change glider orientation or swap for gosper glider gun
	InitGrid(map[Coord]uint64{
		{0, 1}:  2,
		{0, 0}:  1,
		{0, -1}: 7,
	})

	fmt.Println(*GridIn)
	PrintChunkWindow(GridIn, Coord{X: 0, Y: 2}, Coord{X: 2, Y: -5})

	for range 20 {
		time.Sleep(500 * time.Millisecond)
		NextGen()
		PrintChunkWindow(GridOut, Coord{X: 0, Y: 2}, Coord{X: 2, Y: -5})
		SwapGrids()
	}

	fmt.Println(*GridIn)
}
