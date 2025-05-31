import { Text, View } from "react-native"
import MyStyles from "../../styles/MyStyles"
import { useEffect, useState } from "react"
import Apis, { endpoints } from "../../configs/Apis";
import { Chip } from "react-native-paper";
import axios from "axios";


const Home = () => {
  const [medRecord, setMedRecord] = useState([]);
  const [recordDetail, setRecordDetail] = useState([]);

  const loadMedRecord = async () => {
    let res = await axios.get('https://d541-42-115-42-71.ngrok-free.app/medical-records/');
    console.log(res.data)
    setMedRecord(res.data);
  }

  //   const loadMedRecord = async () => {
  //   try {
  //     const response = await axios.get('https://d541-42-115-42-71.ngrok-free.app/medical-records/');
  //     setMedRecord(response.data);
  //   } catch (error) {
  //     console.error(error);
  //   }
  // };

  useEffect(() => {
    loadMedRecord();
  }, [])

  return (
    <View style={[MyStyles.container]}>
      <Text style={MyStyles.subject}> Healthcare app</Text>

      {Array.isArray(medRecord) && medRecord.map(m => (
        <Chip key={m.id} style={[MyStyles.m]}>shit</Chip>
      ))}
    </View>
  );
}

export default Home;