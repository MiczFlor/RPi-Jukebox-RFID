<?php

function phonie_enquene($request)
{
  $measure_round_trip_time = TRUE;
  
  if ($measure_round_trip_time == TRUE)
  {
    $nanotime = exec('date +%s%N');
    $request = array_merge(array('tsp'=>($nanotime)), $request);
  }
  
  $queue = new ZMQSocket(new ZMQContext(), ZMQ::SOCKET_REQ);
  $queue->connect("tcp://127.0.0.1:5555");

  $queue->setSockOpt(ZMQ::SOCKOPT_RCVTIMEO,200);
  $queue->setSockOpt(ZMQ::SOCKOPT_LINGER,200);

  $queue->send(json_encode($request));

  try {  
    $message = $queue->recv();
  } catch (ZMQSocketException $e) {
    /* EAGAIN means that the operation would have blocked, retry */
    /*if ($e->getCode() === ZMQ::ERR_EAGAIN) {
        $message = "Got EAGAIN, retrying \n";
    } else {
        $message = "Error: " . $e->getMessage();
    }*/
    $message = "timeout";
  }    

  ##$queue->close();

  return $message;
}

?>