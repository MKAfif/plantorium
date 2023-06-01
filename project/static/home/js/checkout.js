$(document).ready(function () {
    $('.paywithrazorpay').click(function (e) { 
        e.preventDefault();

        var selects = $("[name='addressId']").val();
        if (selects=="")
        {
            
            swal("Alert", "Address field is needed", "error");
            return false;

        }

        else
        {
            $.ajax({
                method: "GET",
                url: "/proceed-to-pay",
                success: function (response) {

                    var options = {
                        "key": "rzp_test_rYrAv3FDSspvNd", 
                        "amount": response.total * 100, 
                        "currency": "INR",
                        "name": "Plantorium", 
                        "description": "Thank you for Placing an order ",
                        "image": "https://i.pinimg.com/originals/c8/89/90/c88990bf9e98cdcb69a95214e4d28703.jpg",
                        // "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                        // "callback_url": "https://eneqd3r9zrjok.x.pipedream.net/",
                        
                        "handler" : function(responseb){
                            // alert(responseb.Razorpay_payment_id);
                            // $.ajax({
                            //    method: "POST",
                            //     url: "/success",
                            //     data: "data",
                            //     dataType: "dataType",
                            //     success: function (response) {
                                    
                            //     }
                            // });
                            window.location.href = "/razorpay/"+selects;

                        },

                        "prefill": { 
                            "name": "", 
                            "email": "",
                            "contact": "" 
                        },
                        "notes": {
                            "address": "Razorpay Corporate Office"
                        }, 
                        "theme": {
                            "color": "#D19C97"
                        }
                    };
                    var rzp1 = new Razorpay(options);
                    
                    rzp1.open();
        
                   
                    
                }
            });



           
        }


       
           
       
        
    });
});


// testing.............................................

// $(document).ready(function () {
//     $('.paywithrazorpay').click(function (e) { 
//         e.preventDefault();

//         var selects = $("[name='addressId']").val();
//         if (selects == "") {
//             swal("Alert", "Address field is needed", "error");
//             return false;
//         } else {
//             $.ajax({
//                 method: "GET",
//                 url: "/proceed-to-pay",
//                 success: function (response) {
//                     var options = {
//                         "key": "rzp_test_rYrAv3FDSspvNd", 
//                         "amount": 1 * 100, 
//                         "currency": "INR",
//                         "name": "Plantorium", 
//                         "description": "Thank you for Placing an order ",
//                         "image": "https://i.pinimg.com/originals/c8/89/90/c88990bf9e98cdcb69a95214e4d28703.jpg",
//                         "handler": function (responseb) {
//                             alert(responseb.Razorpay_payment_id);
//                             $.ajax({
//                                 method: "POST",
//                                 url: "/success",
//                                 data: "data",
//                                 dataType: "dataType",
//                                 success: function (response) {
//                                     // Save the order in the order database
//                                     $.ajax({
//                                         method: "POST",
//                                         url: "/save-order",
//                                         data: {
//                                             orderData: response  // Pass the necessary order data here
//                                         },
//                                         success: function (orderResponse) {
//                                             // Delete items from the cart
//                                             $.ajax({
//                                                 method: "POST",
//                                                 url: "/delete-cart-items",
//                                                 success: function (cartResponse) {
//                                                     // Redirect to the order page
//                                                     window.location.href = "/order/" + orderResponse.orderId;
//                                                 }
//                                             });
//                                         }
//                                     });
//                                 }
//                             });
//                         },
//                         "prefill": { 
//                             "name": "Gaurav Kumar", 
//                             "email": "gaurav.kumar@example.com",
//                             "contact": "9000090000" 
//                         },
//                         "notes": {
//                             "address": "Razorpay Corporate Office"
//                         }, 
//                         "theme": {
//                             "color": "#D19C97"
//                         }
//                     };
//                     var rzp1 = new Razorpay(options);
//                     rzp1.open();
//                 }
//             });
//         }
//     });
// });
