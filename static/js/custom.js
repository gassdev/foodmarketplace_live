let autocomplete

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
      types: ['geocode', 'establishment'],
      //default in this app is "SN" - add your country code
      componentRestrictions: { country: ['sn'] },
    },
  )
  // function to specify what should happen when the prediction is clicked
  autocomplete.addListener('place_changed', onPlaceChanged)
}

function onPlaceChanged() {
  var place = autocomplete.getPlace()

  // User did not select the prediction. Reset the input field or alert()
  if (!place.geometry) {
    document.getElementById('id_address').placeholder = 'Start typing...'
  } else {
    // console.log('place name=>', place.name)
  }
  // get the address components and assign them to the fields
  //   console.log(place)
  var geocoder = new google.maps.Geocoder()
  var address = document.getElementById('id_address').value

  geocoder.geocode({ address }, function (results, status) {
    // console.log('results ==> ', results)
    // console.log('status ==> ', status)

    if (status == google.maps.GeocoderStatus.OK) {
      var latitude = results[0].geometry.location.lat()
      var longitude = results[0].geometry.location.lng()

      //   console.log('latitude ==> ', latitude)
      //   console.log('longitude ==> ', longitude)

      $('#id_latitude').val(latitude)
      $('#id_longitude').val(longitude)

      $('#id_address').val(address)
    }
  })

  // loop through the address components and assign other address data
  // console.log(place.address_components)
  for (let i = 0; i < place.address_components.length; i++) {
    for (let j = 0; j < place.address_components[i].types.length; j++) {
      // get country
      if (place.address_components[i].types[j] == 'country') {
        $('#id_country').val(place.address_components[i].long_name)
      }

      //   get state
      if (
        place.address_components[i].types[j] == 'administrative_area_level_1'
      ) {
        $('#id_state').val(place.address_components[i].long_name)
      }

      //   get city
      if (place.address_components[i].types[j] == 'locality') {
        $('#id_city').val(place.address_components[i].long_name)
      }

      //   get pincode
      if (place.address_components[i].types[j] == 'postal_code') {
        $('#id_pin_code').val(place.address_components[i].long_name)
      } else {
        $('#id_pin_code').val('')
      }
    }
  }
}

$(document).ready(function () {
  // add to cart
  $('.add-to-cart').on('click', function (e) {
    e.preventDefault()
    let food_id = $(this).attr('data-id')
    let url = $(this).attr('data-url')

    $.ajax({
      type: 'GET',
      url: url,
      success: function (response) {
        if (response.status == 'login_required') {
          swal(response.message, '', 'info').then(function () {
            window.location = '/login'
          })
        } else if (response.status == 'failed') {
          swal(response.message, '', 'error')
        } else {
          $(`#cart-counter`).html(response.cart_counter['cart_count'])
          $(`#qty-${food_id}`).html(response.qty)

          // subtotal, tax and grand total
          applyCartAmounts(
            response.cart_amount['subtotal'],
            response.cart_amount['tax_dict'],
            response.cart_amount['grand_total'],
          )
        }
      },
    })
  })

  // place the cart item quantity on load
  $('.item-qty').each(function () {
    var the_id = $(this).attr('id')
    var qty = $(this).attr('data-qty')
    $(`#${the_id}`).html(qty)
  })

  // decrease cart
  $('.decrease-cart').on('click', function (e) {
    e.preventDefault()
    let food_id = $(this).attr('data-id')
    let url = $(this).attr('data-url')
    let cart_id = $(this).attr('id')

    $.ajax({
      type: 'GET',
      url: url,
      success: function (response) {
        if (response.status == 'login_required') {
          swal(response.message, '', 'info').then(function () {
            window.location = '/login'
          })
        } else if (response.status == 'failed') {
          swal(response.message, '', 'error')
        } else {
          $(`#cart-counter`).html(response.cart_counter['cart_count'])
          $(`#qty-${food_id}`).html(response.qty)

          // subtotal, tax and grand total
          applyCartAmounts(
            response.cart_amount['subtotal'],
            response.cart_amount['tax_dict'],
            response.cart_amount['grand_total'],
          )

          if (window.location.pathname == '/cart/') {
            removeCartItem(response.qty, cart_id)
            checkEmptyCart()
          }
        }
      },
    })
  })

  // DELETE CART ITEM
  $('.delete-cart').on('click', function (e) {
    e.preventDefault()
    let cart_id = $(this).attr('data-id')
    let url = $(this).attr('data-url')

    $.ajax({
      type: 'GET',
      url: url,
      success: function (response) {
        if (response.status == 'failed') {
          swal(response.message, '', 'error')
        } else {
          $(`#cart-counter`).html(response.cart_counter['cart_count'])
          swal(response.status, response.message, 'success')

          // subtotal, tax and grand total
          applyCartAmounts(
            response.cart_amount['subtotal'],
            response.cart_amount['tax_dict'],
            response.cart_amount['grand_total'],
          )

          removeCartItem(0, cart_id)
          checkEmptyCart()
        }
      },
    })
  })

  // delete the cart element if the qty is 0
  function removeCartItem(cartItemQty, cart_id) {
    if (cartItemQty <= 0) {
      // remove the cart item element
      document.getElementById(`cart-item-${cart_id}`).remove()
    }
  }

  // check if the cart is empty
  function checkEmptyCart() {
    var cart_counter = document.getElementById('cart-counter').innerHTML
    if (cart_counter == 0) {
      document.getElementById('empty-cart').style.display = 'block'
    }
  }

  // apply cart amounts
  function applyCartAmounts(subtotal, tax_dict, grand_total) {
    if (window.location.pathname == '/cart/') {
      subtotal = formatAmount(subtotal).toString().replace(/\s/g, ',') // replace space by comma
      // tax = formatAmount(tax).toString().replace(/\s/g, ',')
      grand_total = formatAmount(grand_total).toString().replace(/\s/g, ',')
      $('#subtotal').html(subtotal)
      $('#grand_total').html(grand_total)
      // console.log(tax_dict)
      for (key1 in tax_dict) {
        for (key2 in tax_dict[key1]) {
          tax = formatAmount(tax_dict[key1][key2])
            .toString()
            .replace(/\s/g, ',')
          $(`#tax-${key1}`).html(tax)
        }
      }
    }
  }

  // format amount
  const formatAmount = (amount) => {
    return new Intl.NumberFormat('fr-SN').format(amount)
  }

  // add opening hours
  $('.add_hour').on('click', function (e) {
    e.preventDefault()
    let day = document.getElementById('id_day').value
    let from_hour = document.getElementById('id_from_hour').value
    let to_hour = document.getElementById('id_to_hour').value
    let is_closed = document.getElementById('id_is_closed').checked
    let csrf_token = $('input[name=csrfmiddlewaretoken]').val()
    let url = document.getElementById('add_hour_url').value

    // console.log(day, from_hour, to_hour, is_closed, csrf_token)

    if (is_closed) {
      is_closed = 'True'
      condition = "day != ''"
    } else {
      is_closed = 'False'
      condition = "day != '' && from_hour != '' && to_hour != ''"
    }

    if (eval(condition)) {
      $.ajax({
        type: 'POST',
        url: url,
        data: {
          day: day,
          from_hour: from_hour,
          to_hour: to_hour,
          is_closed: is_closed,
          csrfmiddlewaretoken: csrf_token,
        },
        success: function (response) {
          if (response.status == 'success') {
            if (response.is_closed == 'Closed') {
              html = `<tr id="hour-${response.id}"><td><b>${response.day}</b></td><td>Closed</td><td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/${response.id}/">Remove</a></td></tr>`
            } else {
              html = `<tr id="hour-${response.id}"><td><b>${response.day}</b></td><td>${response.from_hour} - ${response.to_hour}</td><td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/${response.id}/">Remove</a></td></tr>`
            }
            $('.opening-hours').append(html)
            document.getElementById('opening_hours').reset()
          } else {
            swal(response.message, '', 'error')
          }
        },
      })
    } else {
      swal('Please fill all fields', '', 'info')
    }
  })

  // remove opening hours
  $(document).on('click', '.remove_hour', function (e) {
    e.preventDefault()
    url = $(this).attr('data-url')

    $.ajax({
      type: 'GET',
      url: url,
      success: function (response) {
        if (response.status == 'success') {
          document.getElementById(`hour-${response.id}`).remove()
        }
      },
    })
  })

  // document ready close
})
