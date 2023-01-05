// Converting to parquet in Python requires big libraries
const AWS = require('aws-sdk')
const s3 = new AWS.S3()

exports.transform =  async function(event, context) {
   console.log("EVENT: \n" + JSON.stringify(event, null, 2))
   console.log(process.env.BUCKET_NAME)

   var uploadParams = {
      Bucket: process.env.BUCKET_NAME,
      Key: 'test.json',
      Body: JSON.stringify(event),
   };
   
   const data = await s3.upload(uploadParams).promise();

   console.log(data);

   return context.logStreamName
 }