.. _beaglebone-blue-code:

Play with the code
######################

The board has some code built in to the system that can allow you to try
out the various options. They all start with rc

.. code:: bash

   rc_balance            rc_dsm_passthrough    rc_test_encoders
   rc_battery_monitor    rc_kill               rc_test_filters
   rc_benchmark_algebra  rc_spi_loopback       rc_test_imu
   rc_bind_dsm           rc_startup_routine    rc_test_motors
   rc_blink              rc_test_adc           rc_test_polynomial
   rc_calibrate_dsm      rc_test_algebra       rc_test_servos
   rc_calibrate_escs     rc_test_barometer     rc_test_time
   rc_calibrate_gyro     rc_test_buttons       rc_test_vector
   rc_calibrate_mag      rc_test_cape          rc_uart_loopback
   rc_check_battery      rc_test_dmp           rc_version
   rc_check_model        rc_test_drivers       
   rc_cpu_freq           rc_test_dsm         

Try them out to try out the various functions of the board. The source
code for these tests and demos is at `Robotics cape installer at
github <https://github.com/StrawsonDesign/Robotics_Cape_Installer>`__
