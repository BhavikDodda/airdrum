if len(window_R) == WINDOW_SIZE:
                # flatten 50 x 6 → 300
                input_vector = [x for r in window_R for x in r]

                output_R = score_L_stick(input_vector)
                if row_variation(row) > VARTHRESHOLD:
                    predicted = output_R.index(max(output_R))
                    if predicted == 0:      # crash
                        FLOORTOM.stop()
                        CRASH.play()
                        print("Played Crash")
                    elif predicted == 2:    # floortom
                        CRASH.stop()
                        FLOORTOM.play()
                        print("Played FloorTom")